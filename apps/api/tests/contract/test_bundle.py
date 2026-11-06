from __future__ import annotations

import pytest

from tests.helpers import add_article


@pytest.mark.asyncio
async def test_bundle_shape_and_layout(client) -> None:
    for index in range(8):
        await add_article(
            title=f"Bundle story {index}",
            canonical_suffix=f"-b{index}",
            score=10 - index,
        )
    response = await client.get("/v1/news/bundle?industry=legal&locale=en")
    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    for key in (
        "generated_at",
        "language",
        "fallback",
        "total",
        "splash",
        "columns",
        "items",
        "topics",
        "sources",
        "featured",
        "ai_summary",
        "retention_max_age_days",
        "industry",
    ):
        assert key in data, key
    assert data["language"] == "en"
    assert body["meta"]["fallback"] is False
    assert len(data["splash"]) == 3
    assert len(data["columns"]) == 3
    assert data["items"][0]["id"] == data["featured"]["lead"]["id"]
    assert data["total"] == 8
    assert data["industry"]["slug"] == "legal"
    assert data["industry"]["theme"]["layout"] == "editorial"
    assert data["industry"]["cta"]["kind"] == "consultation"
    # R16: which asset a channel offers is channel config, not JSX.
    assert data["industry"]["cta"]["asset"] == "legal-regulatory-calendar"


@pytest.mark.asyncio
async def test_empty_bundle_stays_in_language(client) -> None:
    response = await client.get("/v1/news/bundle?industry=financial&locale=es")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["language"] == "es"
    assert data["fallback"] is False
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_missing_bundle_falls_back_to_english(client) -> None:
    from news_api.platform.db import execute

    await add_article(industry="financial", language="en", title="English fallback story")
    await execute(
        "UPDATE sources SET enabled = FALSE WHERE language = 'es' AND industry_id = "
        "(SELECT id FROM industries WHERE slug = 'financial')"
    )
    response = await client.get("/v1/news/bundle?industry=financial&locale=es")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["language"] == "en"
    assert body["meta"]["fallback"] is True
    assert body["meta"]["language"] == "en"
    assert body["data"]["items"][0]["title"] == "English fallback story"


@pytest.mark.asyncio
async def test_bundle_language_gate(client) -> None:
    await add_article(title="English only", language="en", canonical_suffix="-en")
    await add_article(title="Spanish only", language="es", canonical_suffix="-es")
    english = (await client.get("/v1/news/bundle?industry=legal&locale=en")).json()["data"]
    spanish = (await client.get("/v1/news/bundle?industry=legal&locale=es")).json()["data"]
    assert {item["title"] for item in english["items"]} == {"English only"}
    assert {item["title"] for item in spanish["items"]} == {"Spanish only"}


@pytest.mark.asyncio
async def test_bundle_is_channel_isolated(client) -> None:
    await add_article(industry="legal", title="Same story", canonical_suffix="-iso")
    await add_article(industry="financial", title="Same story", canonical_suffix="-iso")
    legal = (await client.get("/v1/news/bundle?industry=legal&locale=en")).json()["data"]
    financial = (await client.get("/v1/news/bundle?industry=financial&locale=en")).json()["data"]
    assert legal["industry"]["slug"] == "legal"
    assert financial["industry"]["slug"] == "financial"
    assert all(item["title"] == "Same story" for item in legal["items"])
    assert all(item["title"] == "Same story" for item in financial["items"])
    assert {item["id"] for item in legal["items"]}.isdisjoint(
        {item["id"] for item in financial["items"]}
    )
