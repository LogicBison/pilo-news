from __future__ import annotations

import uuid

import pytest

from tests.helpers import add_article


@pytest.mark.asyncio
async def test_admin_login_me_and_csrf(client) -> None:
    login = await client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "test-admin-password"},
    )
    assert login.status_code == 200
    assert "sn_admin" in client.cookies
    csrf = login.json()["csrf_token"]
    client.headers["x-csrf-token"] = csrf

    me = await client.get("/v1/admin/auth/me")
    assert me.status_code == 200
    assert me.json()["operator"]["email"] == "admin@example.com"

    client.headers.pop("x-csrf-token", None)
    no_csrf = await client.post("/v1/admin/refresh", json={"industry": "legal"})
    assert no_csrf.status_code == 403
    assert no_csrf.json()["type"].endswith("/csrf-invalid")


@pytest.mark.asyncio
async def test_admin_login_rejects_bad_password(client) -> None:
    response = await client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_routes_require_auth(client) -> None:
    assert (await client.get("/v1/admin/sources")).status_code == 401
    assert (await client.get("/v1/admin/audit")).status_code == 401
    assert (await client.get("/v1/admin/leads")).status_code == 401


@pytest.mark.asyncio
async def test_source_crud_requires_auth_and_audits(admin_client) -> None:
    feed = f"https://example.org/feed-{uuid.uuid4().hex}.xml"
    created = await admin_client.post(
        "/v1/admin/sources",
        json={
            "industry": "legal",
            "name": "Test feed",
            "feed_url": feed,
            "language": "en",
            "trust": 0.8,
        },
    )
    assert created.status_code == 201
    source_id = created.json()["data"]["id"]

    listed = await admin_client.get("/v1/admin/sources?industry=legal")
    assert any(item["id"] == source_id for item in listed.json()["data"])

    bad = await admin_client.post(
        "/v1/admin/sources",
        json={
            "industry": "legal",
            "name": "Duplicate",
            "feed_url": feed,
            "language": "en",
        },
    )
    assert bad.status_code == 409

    invalid_language = await admin_client.post(
        "/v1/admin/sources",
        json={
            "industry": "legal",
            "name": "French feed",
            "feed_url": f"https://example.org/fr-{uuid.uuid4().hex}.xml",
            "language": "fr",
        },
    )
    assert invalid_language.status_code == 422

    http_url = await admin_client.post(
        "/v1/admin/sources",
        json={
            "industry": "legal",
            "name": "Insecure feed",
            "feed_url": f"http://example.org/http-{uuid.uuid4().hex}.xml",
            "language": "en",
        },
    )
    assert http_url.status_code == 422

    deleted = await admin_client.delete(f"/v1/admin/sources/{source_id}")
    assert deleted.status_code == 204

    audit = await admin_client.get("/v1/admin/audit")
    actions = {item["action"] for item in audit.json()["data"]}
    assert {"source.create", "source.delete"}.issubset(actions)


@pytest.mark.asyncio
async def test_hide_removes_article_from_public(client, admin_client) -> None:
    article = await add_article(title="Hide me", canonical_suffix="-hide")
    visible = await client.get(f"/v1/news/{article['id']}?industry=legal&locale=en")
    assert visible.status_code == 200

    hidden = await admin_client.post(
        f"/v1/admin/articles/{article['id']}/hide", json={"reason": "takedown request"}
    )
    assert hidden.status_code == 200
    assert (
        await client.get(f"/v1/news/{article['id']}?industry=legal&locale=en")
    ).status_code == 404
    bundle = await client.get("/v1/news/bundle?industry=legal&locale=en")
    assert article["id"] not in {item["id"] for item in bundle.json()["data"]["items"]}

    unhidden = await admin_client.post(f"/v1/admin/articles/{article['id']}/unhide")
    assert unhidden.status_code == 200


@pytest.mark.asyncio
async def test_pin_conflict_and_public_promotion(client, admin_client) -> None:
    first = await add_article(title="First pin candidate", canonical_suffix="-p1", score=1)
    second = await add_article(title="Second pin candidate", canonical_suffix="-p2", score=2)
    created = await admin_client.post(
        "/v1/admin/pins",
        json={"article_id": first["id"], "position": 1, "weight": 5},
    )
    assert created.status_code == 201
    conflict = await admin_client.post(
        "/v1/admin/pins",
        json={"article_id": second["id"], "position": 1, "weight": 5},
    )
    assert conflict.status_code == 409

    bundle = await client.get("/v1/news/bundle?industry=legal&locale=en")
    assert bundle.json()["data"]["items"][0]["id"] == first["id"]

    pin_id = created.json()["data"]["id"]
    assert (await admin_client.delete(f"/v1/admin/pins/{pin_id}")).status_code == 204


@pytest.mark.asyncio
async def test_api_key_lifecycle(client, admin_client) -> None:
    created = await admin_client.post(
        "/v1/admin/api-keys", json={"label": "test client", "rate_limit": 600}
    )
    assert created.status_code == 201
    key = created.json()["data"]["key"]
    key_id = created.json()["data"]["id"]
    assert key.startswith("sn_live_")

    public = await client.get("/v1/industries", headers={"x-api-key": key})
    assert public.status_code == 200
    assert public.headers["ratelimit-limit"] == "600"

    revoked = await admin_client.delete(f"/v1/admin/api-keys/{key_id}")
    assert revoked.status_code == 204
    after = await client.get("/v1/industries", headers={"x-api-key": key})
    assert after.status_code == 401
    assert after.json()["type"].endswith("/invalid-key")


@pytest.mark.asyncio
async def test_refresh_trigger_and_status(client, admin_client) -> None:
    response = await admin_client.post("/v1/admin/refresh", json={"industry": "legal"})
    assert response.status_code == 202
    run_id = response.json()["run_id"]
    status = await admin_client.get(f"/v1/admin/refresh/{run_id}")
    assert status.status_code == 200
    assert status.json()["data"]["status"] == "queued"


@pytest.mark.asyncio
async def test_lead_admin_flow(client, admin_client) -> None:
    lead = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "consultation",
            "name": "Lead Person",
            "email": "lead@example.com",
            "phone": "555-0100",
            "message": "Please contact me about a compliance matter.",
            "qualification": "corporate",
            "locale": "en",
            "consent": True,
        },
    )
    assert lead.status_code == 200
    lead_id = lead.json()["id"]

    listed = await admin_client.get("/v1/admin/leads?industry=legal")
    assert any(item["id"] == lead_id for item in listed.json()["data"])

    updated = await admin_client.patch(
        f"/v1/admin/leads/{lead_id}", json={"status": "contacted", "note": "called"}
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "contacted"

    exported = await admin_client.get(f"/v1/admin/leads/{lead_id}/export")
    assert exported.status_code == 200
    assert exported.json()["data"]["email"] == "lead@example.com"

    deleted = await admin_client.delete(f"/v1/admin/leads/{lead_id}")
    assert deleted.status_code == 204
    assert (await admin_client.get(f"/v1/admin/leads/{lead_id}/export")).status_code == 404


@pytest.mark.asyncio
async def test_partner_registry(client, admin_client) -> None:
    listed = await admin_client.get("/v1/admin/partners")
    assert listed.status_code == 200
    assert listed.json()["data"]
    partner = listed.json()["data"][0]
    updated = await admin_client.patch(
        f"/v1/admin/partners/{partner['id']}", json={"status": "disabled"}
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "disabled"


@pytest.mark.asyncio
async def test_admin_funnel_readout(client) -> None:
    assert (await client.get("/v1/admin/funnel")).status_code == 401
    login = await client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "test-admin-password"},
    )
    assert login.status_code == 200
    response = await client.get("/v1/admin/funnel?days=30")
    assert response.status_code == 200
    body = response.json()
    assert body["window_days"] == 30
    assert body["industry"] == "all"
    assert "cta_impression" in body["stages"]
    assert isinstance(body["channels"], list)
    bad = await client.get("/v1/admin/funnel?days=0")
    assert bad.status_code == 400


@pytest.mark.asyncio
async def test_channel_cadence_and_offer_switches(client, admin_client) -> None:
    listed = await admin_client.get("/v1/admin/industries")
    assert listed.status_code == 200
    assert listed.json()["defaults"]["fetch_interval_minutes"] == 720

    updated = await admin_client.patch(
        "/v1/admin/industries/legal",
        json={
            "fetch_interval_minutes": 60,
            "auto_fetch_enabled": False,
            "ai_summaries_enabled": False,
            "offers": {"question": False, "brief": True, "asset": False},
        },
    )
    assert updated.status_code == 200, updated.text
    data = updated.json()["data"]
    assert data["fetch_interval_minutes"] == 60
    assert data["effective_fetch_interval_minutes"] == 60
    assert data["auto_fetch_enabled"] is False
    assert data["ai_summaries_enabled"] is False
    assert data["offers"] == {
        "consultation": True,
        "brief": True,
        "question": False,
        "asset": False,
    }

    public = await client.get("/v1/industries/legal?locale=en")
    assert public.status_code == 200
    assert public.json()["data"]["offers"] == data["offers"]

    bundle = await client.get("/v1/news/bundle?industry=legal&locale=en")
    assert bundle.status_code == 200
    assert bundle.json()["data"]["industry"]["offers"] == data["offers"]

    cleared = await admin_client.patch(
        "/v1/admin/industries/legal",
        json={
            "fetch_interval_minutes": None,
            "auto_fetch_enabled": True,
            "ai_summaries_enabled": True,
        },
    )
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["data"]["fetch_interval_minutes"] is None
    assert cleared.json()["data"]["ai_summaries_enabled"] is True
    assert cleared.json()["data"]["effective_fetch_interval_minutes"] == 720

    too_fast = await admin_client.patch(
        "/v1/admin/industries/legal", json={"fetch_interval_minutes": 3}
    )
    assert too_fast.status_code == 422

    unknown = await admin_client.patch(
        "/v1/admin/industries/legal", json={"offers": {"newsletter": True}}
    )
    assert unknown.status_code == 422

    both = await admin_client.patch(
        "/v1/admin/industries/legal",
        json={"offers": {"brief": True, "asset": True}},
    )
    assert both.status_code == 422
    assert "brief and asset" in both.json()["detail"]

    audit = await admin_client.get("/v1/admin/audit?action=industry.update")
    assert audit.status_code == 200
    assert any(item["entity_id"] == "legal" for item in audit.json()["data"])


@pytest.mark.asyncio
async def test_admin_offer_list_and_dry_run(admin_client, monkeypatch) -> None:
    from news_api.offers.application import build as build_module
    from news_api.offers.domain.models import AdapterResult, RawRecord

    listed = await admin_client.get("/v1/admin/offers")
    assert listed.status_code == 200
    assert listed.json()["data"] == []

    async def fake_fetch(*_args, **_kwargs) -> AdapterResult:
        return AdapterResult(
            records=[
                RawRecord(
                    title="US rule takes effect",
                    date="2026-12-01",
                    jurisdiction="US",
                    action="Takes effect",
                    source_name="Federal Register",
                    source_url="https://www.federalregister.gov/documents/2026/11/01/a",
                    summary="A filing change.",
                )
            ],
            source_version="test-1",
            source_count=1,
        )

    monkeypatch.setattr(build_module, "fetch_records", fake_fetch)
    built = await admin_client.post(
        "/v1/admin/offers/build",
        json={
            "industry": "legal",
            "offer": "legal-regulatory-calendar",
            "issue_date": "2026-11-03",
            "dry_run": True,
        },
    )
    assert built.status_code == 200, built.text
    data = built.json()["data"]
    assert data["status"] == "dry-run"
    assert data["rows"] == 1
    assert data["scope"] == "US"

    from news_api.articles.application import queue

    enqueued: list[dict] = []

    async def fake_enqueue(**kwargs):
        enqueued.append(kwargs)
        return "1-0"

    monkeypatch.setattr(queue, "enqueue_offer", fake_enqueue)
    queued = await admin_client.post(
        "/v1/admin/offers/build",
        json={
            "industry": "legal",
            "offer": "legal-regulatory-calendar",
            "issue_date": "2026-11-03",
        },
    )
    assert queued.status_code == 202, queued.text
    assert queued.json()["status"] == "queued"
    assert enqueued[0]["offer"] == "legal-regulatory-calendar"


@pytest.mark.asyncio
async def test_admin_offer_invalid_id_is_not_found(admin_client) -> None:
    response = await admin_client.get("/v1/admin/offers/not-a-uuid")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ai_settings_default_from_env_and_save_overrides(admin_client) -> None:
    from news_api.platform.settings import get_settings

    env = get_settings()
    read = await admin_client.get("/v1/admin/ai")
    assert read.status_code == 200, read.text
    body = read.json()["data"]
    assert body["defaults"]["ai_monthly_budget_usd"] == env.ai_monthly_budget_usd
    assert body["values"]["ai_monthly_budget_usd"] == env.ai_monthly_budget_usd
    assert body["overridden"] == []
    assert "spent_usd" in body and "remaining_usd" in body
    # Every cap is reported for both buckets, so the panel can show what binds.
    for period in ("day", "month"):
        limits = body["ledger"][period]["limits"]
        assert set(limits) == {"requests", "tokens", "usd"}
        assert set(body["ledger"][period]["remaining"]) == {"requests", "tokens", "usd"}
    assert body["ledger"]["day"]["limits"]["tokens"] == env.ai_daily_token_limit
    assert body["ledger"]["month"]["limits"]["tokens"] == env.ai_monthly_token_limit
    assert body["halted_reason"] is None

    saved = await admin_client.patch(
        "/v1/admin/ai",
        json={
            "ai_monthly_budget_usd": 0.5,
            "ai_daily_budget_usd": 0.25,
            "ai_daily_token_limit": 5_000,
            "ai_max_items_per_run": 9,
            "ai_desks_per_tick": 3,
            "ai_offpeak_only": True,
        },
    )
    assert saved.status_code == 200, saved.text
    data = saved.json()["data"]
    assert data["values"]["ai_monthly_budget_usd"] == 0.5
    assert data["values"]["ai_daily_budget_usd"] == 0.25
    assert data["values"]["ai_daily_token_limit"] == 5_000
    assert data["values"]["ai_max_items_per_run"] == 9
    assert data["values"]["ai_desks_per_tick"] == 3
    assert data["values"]["ai_offpeak_only"] is True
    assert set(data["overridden"]) == {
        "ai_monthly_budget_usd",
        "ai_daily_budget_usd",
        "ai_daily_token_limit",
        "ai_max_items_per_run",
        "ai_desks_per_tick",
        "ai_offpeak_only",
    }
    # The default is still the environment's, and it is still reported.
    assert data["defaults"]["ai_monthly_budget_usd"] == env.ai_monthly_budget_usd
    assert data["ledger"]["day"]["limits"]["tokens"] == 5_000

    again = await admin_client.get("/v1/admin/ai")
    assert again.json()["data"]["values"]["ai_monthly_budget_usd"] == 0.5

    reset = await admin_client.patch("/v1/admin/ai", json={"reset": True})
    assert reset.status_code == 200, reset.text
    assert reset.json()["data"]["overridden"] == []
    assert reset.json()["data"]["values"]["ai_monthly_budget_usd"] == env.ai_monthly_budget_usd


@pytest.mark.asyncio
async def test_ai_settings_reject_bad_values(admin_client) -> None:
    bad_window = await admin_client.patch("/v1/admin/ai", json={"ai_peak_windows": "1-4"})
    assert bad_window.status_code == 422
    bad_budget = await admin_client.patch("/v1/admin/ai", json={"ai_monthly_budget_usd": 0})
    assert bad_budget.status_code == 422
    empty = await admin_client.patch("/v1/admin/ai", json={})
    assert empty.status_code == 422
    # A day cap above the month cap would make the daily knob decorative.
    inverted = await admin_client.patch("/v1/admin/ai", json={"ai_daily_token_limit": 10_000_000})
    assert inverted.status_code == 422
    assert "ai_monthly_token_limit" in inverted.text


@pytest.mark.asyncio
async def test_a_halt_is_reported_and_only_an_operator_clears_it(admin_client) -> None:
    from news_api.articles.infrastructure import ai_budget

    await ai_budget.halt("auth_401")
    read = await admin_client.get("/v1/admin/ai")
    assert read.json()["data"]["halted_reason"] == "auth_401"

    resumed = await admin_client.post("/v1/admin/ai/resume")
    assert resumed.status_code == 200, resumed.text
    assert resumed.json()["data"]["halted_reason"] is None

    audit = await admin_client.get("/v1/admin/audit?action=ai.halt.resume")
    assert audit.status_code == 200
    entries = audit.json()["data"]
    assert entries and entries[0]["payload"]["cleared"] == "auth_401"
