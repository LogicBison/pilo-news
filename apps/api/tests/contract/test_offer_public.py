from __future__ import annotations

from datetime import date

import pytest

from news_api.channels.infrastructure.repo import get_channel
from news_api.offers.infrastructure.repo import upsert_issue


async def make_draft() -> dict:
    channel = await get_channel("legal", enabled_only=False)
    assert channel is not None
    row = await upsert_issue(
        industry_id=channel.id,
        offer_slug="legal-regulatory-calendar",
        issue_date=date(2026, 11, 3),
        scope="US",
        status="draft",
        title="US Regulatory Calendar",
        standfirst="1 dated change. Scope: US.",
        items=[
            {
                "headline": "Rule A takes effect",
                "change": "A filing change.",
                "date": "2026-12-01",
                "jurisdiction": "US",
                "action": "Takes effect",
                "source_name": "Federal Register",
                "source_url": "https://www.federalregister.gov/documents/2026/11/01/a",
            }
        ],
        sources=[
            {
                "name": "Federal Register",
                "url": "https://www.federalregister.gov/documents/2026/11/01/a",
            }
        ],
        source_version="test",
    )
    assert row is not None
    return row


@pytest.mark.asyncio
async def test_publish_unpublish_and_public_reads(client, admin_client) -> None:
    issue = await make_draft()
    issue_id = str(issue["id"])

    empty = await admin_client.post(f"/v1/admin/offers/{issue_id}/publish", json={"reviewer": ""})
    assert empty.status_code == 422

    published = await admin_client.post(
        f"/v1/admin/offers/{issue_id}/publish", json={"reviewer": "Ada Reviewer"}
    )
    assert published.status_code == 200, published.text
    assert published.json()["data"]["status"] == "published"
    assert published.json()["data"]["reviewer"] == "Ada Reviewer"

    listed = await client.get("/v1/industries/legal/references")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1
    assert listed.json()["data"][0]["row_count"] == 1

    detail = await client.get("/v1/industries/legal/references/2026-11-03")
    assert detail.status_code == 200
    assert detail.json()["data"]["reviewer"] == "Ada Reviewer"
    assert detail.json()["data"]["items"][0]["source_url"].startswith("https://")

    missing = await client.get("/v1/industries/legal/references/2026-11-04")
    assert missing.status_code == 404

    unpublished = await admin_client.post(f"/v1/admin/offers/{issue_id}/unpublish")
    assert unpublished.status_code == 200
    assert unpublished.json()["data"]["status"] == "draft"
    assert unpublished.json()["data"]["reviewer"] is None
    assert (await client.get("/v1/industries/legal/references/2026-11-03")).status_code == 404


@pytest.mark.asyncio
async def test_public_reference_is_english_fallback_for_es(client, admin_client) -> None:
    issue = await make_draft()
    await admin_client.post(
        f"/v1/admin/offers/{issue['id']}/publish", json={"reviewer": "Ada Reviewer"}
    )
    response = await client.get("/v1/industries/legal/references?locale=es")
    assert response.status_code == 200
    assert response.json()["meta"]["language"] == "en"
    assert response.json()["meta"]["fallback"] is True
