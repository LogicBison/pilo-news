from __future__ import annotations

from datetime import datetime

from news_api.articles.domain.models import Candidate
from news_api.articles.infrastructure.normalize import article_uuid, canonicalize_url
from news_api.articles.infrastructure.repo import (
    get_summary_state,
    set_article_topics,
    upsert_article,
)
from news_api.channels.infrastructure.repo import get_channel
from news_api.platform.clock import days_ago, hours_ago
from news_api.platform.db import fetch_all, fetch_one


async def industry_id(slug: str = "legal") -> str:
    channel = await get_channel(slug, enabled_only=False)
    assert channel
    return channel.id


async def topic_ids(slugs: list[str], industry: str = "legal") -> list[str]:
    rows = await fetch_all(
        """
        SELECT t.id FROM topics t JOIN industries i ON i.id = t.industry_id
        WHERE i.slug = :slug AND t.slug = ANY(CAST(:slugs AS text[]))
        """,
        {"slug": industry, "slugs": slugs},
    )
    return [str(row["id"]) for row in rows]


async def add_article(
    *,
    industry: str = "legal",
    language: str = "en",
    title: str = "A regulation update for professional readers",
    excerpt: str = "Regulators published a compliance update that changes deadlines.",
    summary: str | None = None,
    status: str = "published",
    published_at: datetime | None = None,
    source_id: str | None = None,
    source_trust: float = 0.9,
    score: float = 1.0,
    topic_slugs: tuple[str, ...] = ("regulation",),
    canonical_suffix: str = "",
) -> dict:
    channel_id = await industry_id(industry)
    url = canonicalize_url(
        f"https://example.com/{industry}/{language}/{title.lower().replace(' ', '-')}{canonical_suffix}"
    )
    candidate = Candidate(
        industry_id=channel_id,
        source_id=source_id,
        source_name="Test Source",
        source_trust=source_trust,
        title=title,
        url=url,
        canonical_url=url,
        excerpt=excerpt,
        publisher="Test Publisher",
        language=language,
        published_at=published_at or hours_ago(2),
        article_id=article_uuid(source_id, url, title),
        score=score,
    )
    article_id, _ = await upsert_article(candidate)
    await set_article_topics(article_id, await topic_ids(list(topic_slugs), industry))
    if summary:
        from news_api.articles.infrastructure.repo import set_summary

        await set_summary(article_id, summary, source="ai", language=language)
    if status != "published":
        from news_api.editorial.infrastructure.ops_repo import set_article_status

        await set_article_status(article_id, status, "test reason")
    row = await fetch_one("SELECT * FROM articles WHERE id = CAST(:id AS uuid)", {"id": article_id})
    assert row
    row["id"] = str(row["id"])
    row["industry_id"] = str(row["industry_id"])
    return row


async def article_state(article_id: str):
    return await get_summary_state(article_id)


def expired_at() -> datetime:
    # Outside the channel visibility window (default 30 days, max 90).
    return days_ago(120)
