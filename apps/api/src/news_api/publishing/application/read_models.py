from __future__ import annotations

from typing import Any

from news_api.channels.domain.theme import Channel
from news_api.platform.cache import get_json
from news_api.platform.clock import now_iso
from news_api.platform.config import scoring_config
from news_api.platform.i18n import normalize_locale
from news_api.publishing.infrastructure import repo


def envelope(data: Any, meta: dict[str, Any]) -> dict[str, Any]:
    return {"data": data, "meta": meta}


def base_meta(
    *,
    request_id: str,
    locale: str,
    language: str,
    fallback: bool,
    next_cursor: str | None = None,
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "locale": locale,
        "language": language,
        "fallback": fallback,
        "generated_at": now_iso(),
        "next_cursor": next_cursor,
    }


async def resolve_language(channel: Channel, locale: str | None) -> tuple[str, str, bool]:
    requested = normalize_locale(locale)
    if requested == "en":
        return requested, "en", False
    exists = await repo.language_exists(channel.id, requested)
    if exists:
        return requested, requested, False
    return requested, "en", True


def retention_days(channel: Channel) -> int:
    """The channel's own window wins; the global scoring value is only a floor.

    Channels are configured by operators (admin or deployment profile); a global
    key must not silently hide content a channel is configured to keep.
    """
    configured = int(scoring_config().get("retention_days", channel.retention_days))
    return max(channel.retention_days, configured)


def card(row: dict[str, Any], topics: list[dict[str, str]]) -> dict[str, Any]:
    published = row["published_at"]
    return {
        "id": str(row["id"]),
        "title": str(row["title"]),
        "summary": row.get("summary"),
        "excerpt": row.get("excerpt"),
        "url": str(row["canonical_url"]),
        "publisher": str(row.get("publisher") or ""),
        "published_at": published.isoformat().replace("+00:00", "Z")
        if hasattr(published, "isoformat")
        else str(published),
        "topics": topics,
        "language": str(row["language"]),
        "verification": str(row.get("verification") or "trusted-source"),
        "corroboration": int(row.get("corroboration") or 1),
    }


async def cards(rows: list[dict[str, Any]], locale: str) -> list[dict[str, Any]]:
    topics = await repo.article_topics_map([str(row["id"]) for row in rows], locale)
    return [card(row, topics.get(str(row["id"]), [])) for row in rows]


async def list_page(
    channel: Channel,
    *,
    locale: str | None,
    limit: int,
    cursor: tuple[float, Any, str] | None,
    topic: str | None,
    query: str | None,
    request_id: str,
) -> dict[str, Any]:
    requested, language, fallback = await resolve_language(channel, locale)
    rows = await repo.list_articles(
        industry_id=channel.id,
        language=language,
        retention_days=retention_days(channel),
        limit=limit,
        topic=topic,
        query=query,
        cursor=cursor,
    )
    has_more = len(rows) > limit
    page = rows[:limit]
    from news_api.platform.pagination import encode_cursor

    next_cursor = None
    if has_more and page:
        last = page[-1]
        next_cursor = encode_cursor(float(last["score"]), last["published_at"], str(last["id"]))
    meta = base_meta(
        request_id=request_id,
        locale=requested,
        language=language,
        fallback=fallback,
        next_cursor=next_cursor,
    )
    return envelope(await cards(page, requested), meta)


async def article_detail(
    channel: Channel, *, locale: str | None, article_id: str, request_id: str
) -> dict[str, Any] | None:
    requested, language, fallback = await resolve_language(channel, locale)
    row = await repo.get_article(
        industry_id=channel.id,
        language=language,
        retention_days=retention_days(channel),
        article_id=article_id,
    )
    if not row:
        return None
    related_rows = await repo.related_articles(
        industry_id=channel.id,
        language=language,
        retention_days=retention_days(channel),
        article_id=article_id,
    )
    item = (await cards([row], requested))[0]
    item["related"] = await cards(related_rows, requested)
    meta = base_meta(request_id=request_id, locale=requested, language=language, fallback=fallback)
    return envelope(item, meta)


async def splash(channel: Channel, *, locale: str | None, request_id: str) -> dict[str, Any]:
    requested, language, fallback = await resolve_language(channel, locale)
    rows = await repo.bundle_articles(
        industry_id=channel.id,
        language=language,
        retention_days=retention_days(channel),
        limit=4,
    )
    items = await cards(rows, requested)
    data = {"lead": items[0] if items else None, "favorites": items[1:4]}
    meta = base_meta(request_id=request_id, locale=requested, language=language, fallback=fallback)
    return envelope(data, meta)


async def bundle(channel: Channel, *, locale: str | None, request_id: str) -> dict[str, Any]:
    rules = scoring_config()
    requested, language, fallback = await resolve_language(channel, locale)
    retention = retention_days(channel)
    max_items = int(rules.get("max_items_per_bundle", 18))
    splash_count = int(rules.get("splash_count", 3))
    column_count = int(rules.get("column_count", 3))
    per_column = int(rules.get("per_column", 4))

    rows = await repo.bundle_articles(
        industry_id=channel.id,
        language=language,
        retention_days=retention,
        limit=max_items,
    )
    items = await cards(rows, requested)
    total = await repo.count_visible(channel.id, language, retention)

    featured_cache = await get_json(f"bundle:featured:{channel.slug}:{language}")
    if isinstance(featured_cache, dict):
        by_id = {item["id"]: item for item in items}
        lead = by_id.get(str(featured_cache.get("lead")))
        favorites = [
            by_id[str(item)] for item in featured_cache.get("favorites", []) if str(item) in by_id
        ][:3]
        if not lead:
            lead = items[0] if items else None
    else:
        lead = items[0] if items else None
        favorites = items[1:4]

    splash_items = items[:splash_count]
    remaining = items[splash_count:]
    columns: list[list[dict[str, Any]]] = [[] for _ in range(column_count)]
    for index, item in enumerate(remaining):
        column = columns[index % column_count]
        if len(column) < per_column:
            column.append(item)
    display = list(splash_items)
    for column in columns:
        display.extend(column)

    brief = await get_json(f"bundle:brief:{channel.slug}:{language}")
    brief_text = brief.get("text") if isinstance(brief, dict) else None
    topics = await repo.topics_with_counts(channel.id, language, retention, requested)
    sources = await repo.public_sources(channel.id, language)

    data = {
        "generated_at": now_iso(),
        "language": language,
        "fallback": fallback,
        "total": total,
        "splash": splash_items,
        "columns": [{"title": None, "items": column} for column in columns],
        "items": display[:max_items],
        "topics": topics,
        "sources": sources,
        "featured": {"lead": lead, "favorites": favorites},
        "ai_summary": brief_text,
        "retention_max_age_days": retention,
        "industry": {
            "slug": channel.slug,
            "name": channel.name,
            "tagline": channel.tagline,
            "theme": channel.theme,
            "disclaimer": channel.disclaimer(requested),
            "cta": channel.cta,
            "timezone": channel.timezone,
        },
    }
    meta = base_meta(request_id=request_id, locale=requested, language=language, fallback=fallback)
    meta["total"] = total
    return envelope(data, meta)


async def topics(channel: Channel, *, locale: str | None, request_id: str) -> dict[str, Any]:
    requested, language, fallback = await resolve_language(channel, locale)
    data = await repo.topics_with_counts(channel.id, language, retention_days(channel), requested)
    meta = base_meta(request_id=request_id, locale=requested, language=language, fallback=fallback)
    return envelope(data, meta)


async def sources(channel: Channel, *, locale: str | None, request_id: str) -> dict[str, Any]:
    requested, language, fallback = await resolve_language(channel, locale)
    data = await repo.public_sources(channel.id, language)
    meta = base_meta(request_id=request_id, locale=requested, language=language, fallback=fallback)
    return envelope(data, meta)
