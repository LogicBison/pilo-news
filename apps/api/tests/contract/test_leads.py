from __future__ import annotations

import pytest

from tests.helpers import add_article


@pytest.mark.asyncio
async def test_contact_happy_path_and_duplicate(client) -> None:
    payload = {
        "name": "Test Person",
        "email": "person@example.com",
        "message": "I would like to learn more about the compliance briefing.",
        "locale": "en",
        "industry": "legal",
    }
    first = await client.post("/v1/contact", json=payload)
    assert first.status_code == 200
    assert first.json()["id"]
    duplicate = await client.post("/v1/contact", json=payload)
    assert duplicate.status_code == 200
    assert duplicate.json() == {"status": "received"}


@pytest.mark.asyncio
async def test_contact_validation_and_honeypot(client) -> None:
    bad = await client.post(
        "/v1/contact",
        json={
            "name": "A",
            "email": "not-an-email",
            "message": "short",
            "locale": "en",
            "industry": "legal",
        },
    )
    assert bad.status_code == 422
    honeypot = await client.post(
        "/v1/contact",
        json={
            "name": "Bot",
            "email": "bot@example.com",
            "message": "This is a spam message for the contact form.",
            "locale": "en",
            "industry": "legal",
            "website": "https://spam.example",
        },
    )
    assert honeypot.status_code == 200
    assert honeypot.json() == {"status": "received"}


@pytest.mark.asyncio
async def test_contact_rate_limit(client) -> None:
    from news_api.platform.settings import get_settings

    settings = get_settings()
    original = settings.contact_rate_limit_per_hour
    settings.contact_rate_limit_per_hour = 1
    try:
        base = {
            "name": "Test Person",
            "message": "This is a valid contact message for the team.",
            "locale": "en",
            "industry": "legal",
        }
        first = await client.post("/v1/contact", json={**base, "email": "a@example.com"})
        assert first.status_code == 200
        second = await client.post("/v1/contact", json={**base, "email": "b@example.com"})
        assert second.status_code == 429
        assert second.headers["retry-after"]
    finally:
        settings.contact_rate_limit_per_hour = original


@pytest.mark.asyncio
async def test_lead_requires_consent(client) -> None:
    response = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "consultation",
            "name": "Test Person",
            "email": "person@example.com",
            "message": "I need help with a compliance review.",
            "locale": "en",
            "consent": False,
        },
    )
    assert response.status_code == 422
    assert response.json()["type"].endswith("/validation")


@pytest.mark.asyncio
async def test_lead_created_without_pii_echo(client) -> None:
    article = await add_article(title="Lead magnet story")
    response = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "consultation",
            "name": "Private Person",
            "email": "private@example.com",
            "qualification": "corporate",
            "phone": "555-0100",
            "company": "Acme",
            "message": "Please contact me about the compliance briefing.",
            "locale": "en",
            "consent": True,
            "article_id": article["id"],
            "utm": {"utm_source": "test"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body).issubset({"id", "status"})
    text = response.text
    assert "private@example.com" not in text
    assert "Private Person" not in text
    assert "555-0100" not in text

    duplicate = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "consultation",
            "name": "Private Person",
            "email": "private@example.com",
            "qualification": "corporate",
            "message": "Please contact me about the compliance briefing.",
            "locale": "en",
            "consent": True,
        },
    )
    assert duplicate.status_code == 200
    assert duplicate.json() == {"status": "received"}


@pytest.mark.asyncio
async def test_logistics_requires_phone_and_company(client) -> None:
    response = await client.post(
        "/v1/leads",
        json={
            "industry": "logistics",
            "kind": "consultation",
            "name": "Ops Lead",
            "email": "ops@example.com",
            "message": "We need capacity on the Asia to US lane.",
            "locale": "en",
            "consent": True,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_lead_rate_limit(client) -> None:
    from news_api.platform.settings import get_settings

    settings = get_settings()
    original = settings.lead_rate_limit_per_hour
    settings.lead_rate_limit_per_hour = 1
    try:
        base = {
            "industry": "education",
            "kind": "brief",
            "name": "Reader",
            "message": "Send the weekly brief.",
            "locale": "en",
            "consent": True,
            "qualification": "certificate",
        }
        first = await client.post("/v1/leads", json={**base, "email": "one@example.com"})
        assert first.status_code == 200
        second = await client.post("/v1/leads", json={**base, "email": "two@example.com"})
        assert second.status_code == 429
    finally:
        settings.lead_rate_limit_per_hour = original


@pytest.mark.asyncio
async def test_lead_qualification_is_validated_and_accepted(client) -> None:
    base = {
        "industry": "legal",
        "kind": "consultation",
        "name": "Qualified Person",
        "email": "qualified@example.com",
        "message": "Please contact me about a corporate matter.",
        "locale": "en",
        "consent": True,
    }
    missing = await client.post("/v1/leads", json=base)
    assert missing.status_code == 422

    invalid = await client.post("/v1/leads", json={**base, "qualification": "not-a-real-option"})
    assert invalid.status_code == 422

    accepted = await client.post("/v1/leads", json={**base, "qualification": "corporate"})
    assert accepted.status_code == 200
    assert accepted.json()["id"]

    brief = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "brief",
            "name": "Brief Person",
            "email": "brief@example.com",
            "locale": "en",
            "consent": True,
        },
    )
    assert brief.status_code == 200

    # the brief rung stays two fields: no qualification required, and a provided one is still validated
    brief_with_bad_option = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "brief",
            "name": "Brief Two",
            "email": "brief2@example.com",
            "locale": "en",
            "consent": True,
            "qualification": "not-a-real-option",
        },
    )
    assert brief_with_bad_option.status_code == 422


@pytest.mark.asyncio
async def test_question_and_asset_rungs(client) -> None:
    question = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "question",
            "name": "Curious Reader",
            "email": "reader@example.com",
            "message": "Does the new AI Act guidance change client disclosure duties?",
            "locale": "en",
            "consent": True,
        },
    )
    assert question.status_code == 200
    assert set(question.json()).issubset({"id", "status"})

    asset = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "asset",
            "asset": "legal-regulatory-calendar",
            "name": "Calendar Reader",
            "email": "calendar@example.com",
            "locale": "en",
            "consent": True,
        },
    )
    assert asset.status_code == 200
    assert set(asset.json()).issubset({"id", "status"})


@pytest.mark.asyncio
async def test_disposable_email_is_rejected(client) -> None:
    response = await client.post(
        "/v1/leads",
        json={
            "industry": "legal",
            "kind": "consultation",
            "name": "Throwaway Person",
            "email": "throwaway@mailinator.com",
            "message": "Please contact me about a compliance review today.",
            "locale": "en",
            "consent": True,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_contact_stores_attribution_without_raw_ip(client) -> None:
    from news_api.platform.db import fetch_one
    from news_api.platform.settings import get_settings

    settings = get_settings()
    original = settings.geo_country_header
    settings.geo_country_header = "cf-ipcountry"
    try:
        response = await client.post(
            "/v1/contact",
            headers={"cf-ipcountry": "us"},
            json={
                "name": "Attribution Person",
                "email": "attribution@example.com",
                "message": "Please send the compliance briefing.",
                "locale": "en",
                "industry": "legal",
                "source_page": "/legal/contact",
                "utm": {"utm_source": "newsletter", "utm_unknown": "drop"},
                "session_hash": "session-123",
            },
        )
        assert response.status_code == 200, response.text
        contact = await fetch_one(
            "SELECT * FROM contact_messages WHERE id = CAST(:id AS uuid)",
            {"id": response.json()["id"]},
        )
        assert contact is not None
        assert contact["country"] == "US"
        assert contact["source_page"] == "/legal/contact"
        assert contact["utm"] == {"utm_source": "newsletter"}
        assert contact["session_hash"] and contact["session_hash"] != "session-123"
        assert contact["ip_hash"] and contact["ua_hash"]
    finally:
        settings.geo_country_header = original


@pytest.mark.asyncio
async def test_lead_stores_country_session_and_clean_utm(client, admin_client) -> None:
    from news_api.platform.settings import get_settings

    settings = get_settings()
    original = settings.geo_country_header
    settings.geo_country_header = "cf-ipcountry"
    try:
        response = await client.post(
            "/v1/leads",
            headers={"cf-ipcountry": "ca"},
            json={
                "industry": "legal",
                "kind": "consultation",
                "name": "Attribution Lead",
                "email": "lead-attribution@example.com",
                "message": "I need a compliance review.",
                "locale": "en",
                "consent": True,
                "qualification": "corporate",
                "source_page": "/legal",
                "utm": {"utm_medium": "referral", "utm_unknown": "drop"},
                "session_hash": "session-456",
            },
        )
        assert response.status_code == 200, response.text
        lead_id = response.json()["id"]
        listed = await admin_client.get("/v1/admin/leads?industry=legal")
        lead = next(item for item in listed.json()["data"] if item["id"] == lead_id)
        assert lead["country"] == "CA"
        assert lead["utm"] == {"utm_medium": "referral"}
        assert lead["session_hash"] and lead["session_hash"] != "session-456"
    finally:
        settings.geo_country_header = original


@pytest.mark.asyncio
async def test_admin_contact_inbox_and_erase(client, admin_client) -> None:
    created = await client.post(
        "/v1/contact",
        json={
            "name": "Inbox Person",
            "email": "inbox@example.com",
            "message": "Please send this to the desk.",
            "locale": "en",
            "industry": "legal",
            "source_page": "/legal/contact",
        },
    )
    assert created.status_code == 200
    contact_id = created.json()["id"]

    listed = await admin_client.get("/v1/admin/contacts?industry=legal")
    assert listed.status_code == 200
    row = next(item for item in listed.json()["data"] if item["id"] == contact_id)
    assert row["source_page"] == "/legal/contact"
    assert row["status"] == "new"

    updated = await admin_client.patch(f"/v1/admin/contacts/{contact_id}", json={"status": "read"})
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "read"

    deleted = await admin_client.delete(f"/v1/admin/contacts/{contact_id}")
    assert deleted.status_code == 204
    assert (
        await admin_client.patch(f"/v1/admin/contacts/{contact_id}", json={"status": "closed"})
    ).status_code == 404
