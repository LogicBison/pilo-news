from __future__ import annotations

import uuid

import pytest

from tests.helpers import add_article, expired_at


@pytest.mark.asyncio
async def test_list_industries_returns_five_channels(client) -> None:
    response = await client.get("/v1/industries")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 5
    slugs = {item["slug"] for item in body["data"]}
    assert slugs == {"legal", "financial", "behavioral-health", "education", "logistics"}
    assert body["meta"]["request_id"]


@pytest.mark.asyncio
async def test_industry_detail_and_unknown(client) -> None:
    response = await client.get("/v1/industries/legal?locale=es")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["slug"] == "legal"
    assert data["theme_summary"]["layout"] == "editorial"
    assert "Noticias" in data["disclaimer"]
    missing = await client.get("/v1/industries/nope")
    assert missing.status_code == 404
    assert missing.json()["type"].endswith("/not-found")


@pytest.mark.asyncio
async def test_disabled_channel_is_404(client) -> None:
    from news_api.channels.infrastructure.repo import update_channel
    from news_api.platform.db import execute

    await add_article(industry="education", language="en", title="Education policy update")
    await update_channel("education", enabled=False)
    try:
        assert (await client.get("/v1/industries/education")).status_code == 404
        assert (await client.get("/v1/news?industry=education&locale=en")).status_code == 404
    finally:
        await execute("UPDATE industries SET enabled = TRUE WHERE slug = 'education'")


@pytest.mark.asyncio
async def test_news_list_is_language_and_channel_isolated(client) -> None:
    await add_article(title="Legal English one", language="en", canonical_suffix="-1")
    await add_article(title="Legal English two", language="en", canonical_suffix="-2")
    await add_article(title="Legal Spanish one", language="es", canonical_suffix="-3")
    await add_article(industry="financial", title="Financial English", language="en")

    response = await client.get("/v1/news?industry=legal&locale=en&limit=50")
    assert response.status_code == 200
    body = response.json()
    titles = [item["title"] for item in body["data"]]
    assert "Legal English one" in titles
    assert "Legal Spanish one" not in titles
    assert "Financial English" not in titles
    assert all(item["language"] == "en" for item in body["data"])
    assert body["meta"]["language"] == "en"
    assert body["meta"]["fallback"] is False

    spanish = await client.get("/v1/news?industry=legal&locale=es")
    assert spanish.status_code == 200
    assert [item["title"] for item in spanish.json()["data"]] == ["Legal Spanish one"]


@pytest.mark.asyncio
async def test_news_list_excludes_hidden_expired_and_disabled_source(client) -> None:
    from news_api.sources.infrastructure.repo import (
        create_source,
        update_source,
    )

    visible = await add_article(title="Visible story", canonical_suffix="-v")
    await add_article(title="Hidden story", status="hidden", canonical_suffix="-h")
    await add_article(title="Expired story", published_at=expired_at(), canonical_suffix="-e")
    source = await create_source(
        industry_id=visible["industry_id"],
        name="Disabled source",
        feed_url=f"https://example.org/disabled-{uuid.uuid4().hex}.xml",
        language="en",
        trust=0.9,
        enabled=True,
        allow_http=False,
        poll_interval_min=720,
        terms_checked_at=None,
        terms_url=None,
    )
    assert source is not None
    await add_article(
        title="Disabled source story",
        source_id=source.id,
        canonical_suffix="-d",
    )
    await update_source(source.id, {"enabled": False})

    response = await client.get("/v1/news?industry=legal&locale=en&limit=50")
    titles = [item["title"] for item in response.json()["data"]]
    assert titles == ["Visible story"]


@pytest.mark.asyncio
async def test_news_list_validation_and_cursor(client) -> None:
    for index in range(3):
        await add_article(
            title=f"Cursored story {index}", canonical_suffix=f"-c{index}", score=3 - index
        )
    first = await client.get("/v1/news?industry=legal&locale=en&limit=1")
    assert first.status_code == 200
    next_cursor = first.json()["meta"]["next_cursor"]
    assert next_cursor
    second = await client.get(f"/v1/news?industry=legal&locale=en&limit=1&cursor={next_cursor}")
    assert second.status_code == 200
    assert second.json()["data"][0]["id"] != first.json()["data"][0]["id"]

    assert (await client.get("/v1/news?industry=legal&locale=fr")).status_code == 400
    assert (await client.get("/v1/news?industry=legal&bogus=1")).status_code == 400
    assert (await client.get("/v1/news?industry=legal&limit=500")).status_code == 400
    assert (await client.get("/v1/news?industry=legal&q=x")).status_code == 400
    assert (await client.get("/v1/news?locale=en")).status_code == 400


@pytest.mark.asyncio
async def test_article_detail_and_related(client) -> None:
    article = await add_article(title="Detail story", canonical_suffix="-detail")
    await add_article(title="Related English", language="en", canonical_suffix="-r1")
    await add_article(title="Related Spanish", language="es", canonical_suffix="-r2")

    response = await client.get(f"/v1/news/{article['id']}?industry=legal&locale=en")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Detail story"
    assert data["related"]
    assert all(item["language"] == "en" for item in data["related"])

    missing = await client.get(
        "/v1/news/00000000-0000-0000-0000-000000000000?industry=legal&locale=en"
    )
    assert missing.status_code == 404

    hidden = await add_article(title="Hidden detail", status="hidden", canonical_suffix="-hd")
    assert (
        await client.get(f"/v1/news/{hidden['id']}?industry=legal&locale=en")
    ).status_code == 404


@pytest.mark.asyncio
async def test_splash_empty_channel_is_valid(client) -> None:
    response = await client.get("/v1/news/splash?industry=behavioral-health&locale=en")
    assert response.status_code == 200
    assert response.json()["data"]["lead"] is None
    assert response.json()["data"]["favorites"] == []


@pytest.mark.asyncio
async def test_etag_returns_304_with_empty_body(client) -> None:
    await add_article(title="ETag story", canonical_suffix="-etag")
    first = await client.get("/v1/news/bundle?industry=legal&locale=en")
    etag = first.headers["etag"]
    assert etag.startswith('W/"')
    second = await client.get(
        "/v1/news/bundle?industry=legal&locale=en", headers={"if-none-match": etag}
    )
    assert second.status_code == 304
    assert second.content == b""


@pytest.mark.asyncio
async def test_unknown_locale_and_query_params(client) -> None:
    response = await client.get("/v1/industries?locale=fr")
    assert response.status_code == 400
    assert response.json()["type"].endswith("/invalid-locale")
    response = await client.get("/v1/industries?foo=bar")
    assert response.status_code == 400
    assert response.json()["type"].endswith("/invalid-query")
