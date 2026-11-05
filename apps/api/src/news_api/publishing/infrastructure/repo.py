from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from news_api.platform.db import fetch_all, fetch_one, session_scope
from news_api.platform.jsons import as_dict

VISIBLE_GUARD = """
    a.status = 'published'
    AND a.language = :language
    AND (a.source_id IS NULL OR s.enabled = TRUE)
    AND (a.is_seed = TRUE OR a.published_at >= now() - make_interval(days => :retention_days))
"""


def _article_select() -> str:
    return """
    SELECT a.id, a.title, a.excerpt, a.summary, a.canonical_url, a.publisher,
           a.published_at, a.language, a.corroboration, a.corroborating_sources,
           a.verification, a.is_seed, a.score
    FROM articles a
    LEFT JOIN sources s ON s.id = a.source_id
    """


async def language_exists(industry_id: str, language: str) -> bool:
    if language == "en":
        return True
    row = await fetch_one(
        """
        SELECT
            EXISTS (SELECT 1 FROM sources WHERE industry_id = CAST(:industry_id AS uuid)
                    AND language = :language AND enabled = TRUE) AS has_source,
            EXISTS (SELECT 1 FROM articles WHERE industry_id = CAST(:industry_id AS uuid)
                    AND language = :language) AS has_article
        """,
        {"industry_id": industry_id, "language": language},
    )
    return bool(row and (row["has_source"] or row["has_article"]))


async def count_visible(industry_id: str, language: str, retention_days: int) -> int:
    row = await fetch_one(
        f"""
        SELECT COUNT(*) AS total FROM articles a
        LEFT JOIN sources s ON s.id = a.source_id
        WHERE a.industry_id = CAST(:industry_id AS uuid) AND {VISIBLE_GUARD}
        """,
        {
            "industry_id": industry_id,
            "language": language,
            "retention_days": retention_days,
        },
    )
    return int(row["total"]) if row else 0


def _filters(
    *,
    industry_id: str,
    language: str,
    retention_days: int,
    topic: str | None,
    query: str | None,
    cursor: tuple[float, Any, str] | None,
) -> tuple[str, dict[str, Any]]:
    clauses = [VISIBLE_GUARD]
    params: dict[str, Any] = {
        "industry_id": industry_id,
        "language": language,
        "retention_days": retention_days,
    }
    if topic:
        clauses.append(
            """
            EXISTS (
                SELECT 1 FROM article_topics at
                JOIN topics t ON t.id = at.topic_id
                WHERE at.article_id = a.id AND t.slug = :topic
            )
            """
        )
        params["topic"] = topic
    if query:
        clauses.append("a.search_vector @@ websearch_to_tsquery('simple', :query)")
        params["query"] = query
    if cursor:
        clauses.append(
            "(a.score, a.published_at, a.id) < "
            "(:cursor_score, :cursor_published, CAST(:cursor_id AS uuid))"
        )
        params["cursor_score"] = cursor[0]
        params["cursor_published"] = cursor[1]
        params["cursor_id"] = cursor[2]
    return " AND ".join(clauses), params


async def list_articles(
    *,
    industry_id: str,
    language: str,
    retention_days: int,
    limit: int,
    topic: str | None = None,
    query: str | None = None,
    cursor: tuple[float, Any, str] | None = None,
) -> list[dict[str, Any]]:
    where, params = _filters(
        industry_id=industry_id,
        language=language,
        retention_days=retention_days,
        topic=topic,
        query=query,
        cursor=cursor,
    )
    params["limit"] = limit + 1
    rows = await fetch_all(
        f"""
        {_article_select()}
        WHERE a.industry_id = CAST(:industry_id AS uuid) AND {where}
        ORDER BY a.score DESC, a.published_at DESC, a.id DESC
        LIMIT :limit
        """,
        params,
    )
    return rows


async def get_article(
    *, industry_id: str, language: str, retention_days: int, article_id: str
) -> dict[str, Any] | None:
    where, params = _filters(
        industry_id=industry_id,
        language=language,
        retention_days=retention_days,
        topic=None,
        query=None,
        cursor=None,
    )
    params["article_id"] = article_id
    return await fetch_one(
        f"""
        {_article_select()}
        WHERE a.industry_id = CAST(:industry_id AS uuid) AND a.id = CAST(:article_id AS uuid)
          AND {where}
        """,
        params,
    )


async def related_articles(
    *,
    industry_id: str,
    language: str,
    retention_days: int,
    article_id: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    rows = await fetch_all(
        f"""
        {_article_select()}
        WHERE a.industry_id = CAST(:industry_id AS uuid)
          AND a.id <> CAST(:article_id AS uuid)
          AND {VISIBLE_GUARD}
        ORDER BY a.score DESC, a.published_at DESC, a.id DESC
        LIMIT :limit
        """,
        {
            "industry_id": industry_id,
            "article_id": article_id,
            "language": language,
            "retention_days": retention_days,
            "limit": limit,
        },
    )
    return rows


async def bundle_articles(
    *, industry_id: str, language: str, retention_days: int, limit: int
) -> list[dict[str, Any]]:
    rows = await fetch_all(
        f"""
        {_article_select()}
        LEFT JOIN pins p ON p.article_id = a.id AND p.pin_expires_at > now()
        WHERE a.industry_id = CAST(:industry_id AS uuid) AND {VISIBLE_GUARD}
        ORDER BY (p.id IS NOT NULL) DESC, p.position ASC NULLS LAST,
                 a.score DESC, a.published_at DESC, a.id DESC
        LIMIT :limit
        """,
        {
            "industry_id": industry_id,
            "language": language,
            "retention_days": retention_days,
            "limit": limit,
        },
    )
    return rows


async def article_topics_map(
    article_ids: list[str], locale: str
) -> dict[str, list[dict[str, str]]]:
    if not article_ids:
        return {}
    rows = await fetch_all(
        """
        SELECT at.article_id::text AS article_id, t.slug, t.label
        FROM article_topics at
        JOIN topics t ON t.id = at.topic_id
        WHERE at.article_id::text = ANY(CAST(:ids AS text[]))
        ORDER BY t.weight DESC, t.slug
        """,
        {"ids": list(article_ids)},
    )
    result: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        label = as_dict(row.get("label"))
        localized = str(label.get(locale) or label.get("en") or row["slug"])
        result.setdefault(str(row["article_id"]), []).append(
            {"slug": str(row["slug"]), "label": localized}
        )
    return result


async def topics_with_counts(
    industry_id: str, language: str, retention_days: int, locale: str
) -> list[dict[str, Any]]:
    rows = await fetch_all(
        """
        SELECT t.slug, t.label, t.weight,
               COUNT(a.id) AS total
        FROM topics t
        LEFT JOIN article_topics at ON at.topic_id = t.id
        LEFT JOIN articles a ON a.id = at.article_id
            AND a.status = 'published'
            AND a.language = :language
            AND (a.is_seed = TRUE OR a.published_at >= now() - make_interval(days => :days))
        WHERE t.industry_id = CAST(:industry_id AS uuid)
        GROUP BY t.id, t.slug, t.label, t.weight
        ORDER BY t.weight DESC, t.slug
        """,
        {
            "industry_id": industry_id,
            "language": language,
            "days": retention_days,
        },
    )
    result = []
    for row in rows:
        label = as_dict(row.get("label"))
        result.append(
            {
                "slug": str(row["slug"]),
                "label": str(label.get(locale) or label.get("en") or row["slug"]),
                "weight": float(row["weight"]),
                "count": int(row["total"]),
            }
        )
    return result


async def public_sources(industry_id: str, language: str | None = None) -> list[dict[str, Any]]:
    guard = " AND language = :language" if language else ""
    params: dict[str, Any] = {"industry_id": industry_id}
    if language:
        params["language"] = language
    rows = await fetch_all(
        f"""
        SELECT name, feed_url, language FROM sources
        WHERE industry_id = CAST(:industry_id AS uuid) AND enabled = TRUE{guard}
        ORDER BY name
        """,
        params,
    )
    return [
        {"name": str(row["name"]), "url": str(row["feed_url"]), "language": row["language"]}
        for row in rows
    ]


async def insert_contact(
    *,
    industry_id: str | None,
    name: str,
    email: str,
    phone: str | None,
    message: str,
    locale: str,
) -> str:
    row = await fetch_one(
        """
        INSERT INTO contact_messages (industry_id, name, email, phone, message, locale)
        VALUES (CAST(:industry_id AS uuid), :name, :email, :phone, :message, :locale)
        RETURNING id
        """,
        {
            "industry_id": industry_id,
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
            "locale": locale,
        },
    )
    if not row:
        raise RuntimeError("contact insert failed")
    return str(row["id"])


async def insert_cta_event(
    *,
    industry_id: str,
    event: str,
    placement: str,
    locale: str,
    article_id: str | None,
    session_hash: str,
    result: str | None,
) -> None:
    async with session_scope() as session:
        await session.execute(
            text(
                """
                INSERT INTO cta_events (
                    industry_id, event, placement, locale, article_id, session_hash, result
                ) VALUES (
                    CAST(:industry_id AS uuid), :event, :placement, :locale,
                    CAST(:article_id AS uuid), :session_hash, :result
                )
                """
            ),
            {
                "industry_id": industry_id,
                "event": event,
                "placement": placement,
                "locale": locale,
                "article_id": article_id,
                "session_hash": session_hash,
                "result": result,
            },
        )


async def recent_contact_count(industry_id: str | None, email: str, minutes: int = 10) -> int:
    row = await fetch_one(
        """
        SELECT COUNT(*) AS total FROM contact_messages
        WHERE COALESCE(industry_id::text, '') = COALESCE(:industry_id, '')
          AND lower(email) = lower(:email)
          AND created_at >= now() - make_interval(mins => :minutes)
        """,
        {"industry_id": industry_id, "email": email, "minutes": minutes},
    )
    return int(row["total"]) if row else 0


def json_dumps(value: Any) -> str:
    return json.dumps(value, default=str)
