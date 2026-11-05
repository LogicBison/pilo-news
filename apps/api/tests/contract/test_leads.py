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
        }
        first = await client.post("/v1/leads", json={**base, "email": "one@example.com"})
        assert first.status_code == 200
        second = await client.post("/v1/leads", json={**base, "email": "two@example.com"})
        assert second.status_code == 429
    finally:
        settings.lead_rate_limit_per_hour = original
