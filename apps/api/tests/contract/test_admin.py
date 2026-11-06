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
