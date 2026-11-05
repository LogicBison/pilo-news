from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from news_api.platform.db import fetch_all, fetch_one, session_scope
from news_api.sources.domain.models import Source, source_from_row

COLUMNS = """
id, industry_id, name, feed_url, language, trust, enabled, allow_http, poll_interval_min,
terms_checked_at, terms_url, etag, last_modified, last_fetched_at, last_success_at,
status, consecutive_failures, last_error
"""


async def list_sources(
    industry_id: str | None = None, *, include_disabled: bool = True
) -> list[Source]:
    clauses: list[str] = []
    params: dict[str, Any] = {}
    if industry_id:
        clauses.append("industry_id = :industry_id")
        params["industry_id"] = industry_id
    if not include_disabled:
        clauses.append("enabled = TRUE")
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = await fetch_all(f"SELECT {COLUMNS} FROM sources{where} ORDER BY name", params)
    return [source_from_row(row) for row in rows]


async def get_source(source_id: str) -> Source | None:
    row = await fetch_one(f"SELECT {COLUMNS} FROM sources WHERE id = :id", {"id": source_id})
    return source_from_row(row) if row else None


async def list_fetchable(
    language: str | None = None, industry_id: str | None = None
) -> list[Source]:
    clauses = ["enabled = TRUE", "status = 'active'"]
    params: dict[str, Any] = {}
    if language:
        clauses.append("language = :language")
        params["language"] = language
    if industry_id:
        clauses.append("industry_id = :industry_id")
        params["industry_id"] = industry_id
    rows = await fetch_all(
        f"SELECT {COLUMNS} FROM sources WHERE {' AND '.join(clauses)} ORDER BY name",
        params,
    )
    return [source_from_row(row) for row in rows]


async def create_source(
    *,
    industry_id: str,
    name: str,
    feed_url: str,
    language: str,
    trust: float,
    enabled: bool,
    allow_http: bool,
    poll_interval_min: int,
    terms_checked_at: str | None,
    terms_url: str | None,
) -> Source | None:
    row = await fetch_one(
        f"""
        INSERT INTO sources (
            industry_id, name, feed_url, language, trust, enabled, allow_http,
            poll_interval_min, terms_checked_at, terms_url
        ) VALUES (
            :industry_id, :name, :feed_url, :language, :trust, :enabled, :allow_http,
            :poll_interval_min, :terms_checked_at, :terms_url
        )
        ON CONFLICT (industry_id, feed_url) DO NOTHING
        RETURNING {COLUMNS}
        """,
        {
            "industry_id": industry_id,
            "name": name,
            "feed_url": feed_url,
            "language": language,
            "trust": trust,
            "enabled": enabled,
            "allow_http": allow_http,
            "poll_interval_min": poll_interval_min,
            "terms_checked_at": terms_checked_at,
            "terms_url": terms_url,
        },
    )
    return source_from_row(row) if row else None


async def update_source(source_id: str, fields: dict[str, Any]) -> Source | None:
    allowed = {
        "name",
        "feed_url",
        "language",
        "trust",
        "enabled",
        "allow_http",
        "poll_interval_min",
        "terms_checked_at",
        "terms_url",
        "status",
    }
    assignments = [f"{key} = :{key}" for key in fields if key in allowed]
    if not assignments:
        return await get_source(source_id)
    assignments.append("updated_at = now()")
    params = {key: value for key, value in fields.items() if key in allowed}
    params["id"] = source_id
    row = await fetch_one(
        f"UPDATE sources SET {', '.join(assignments)} WHERE id = :id RETURNING {COLUMNS}",
        params,
    )
    return source_from_row(row) if row else None


async def delete_source(source_id: str) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text("DELETE FROM sources WHERE id = :id"), {"id": source_id}
        )
        return bool(getattr(result, "rowcount", 0))


async def record_fetch_result(
    source_id: str,
    *,
    success: bool,
    etag: str | None = None,
    last_modified: str | None = None,
    error: str | None = None,
    blocked: bool = False,
) -> None:
    async with session_scope() as session:
        if success:
            await session.execute(
                text(
                    """
                    UPDATE sources SET
                        last_fetched_at = now(),
                        last_success_at = now(),
                        etag = COALESCE(:etag, etag),
                        last_modified = COALESCE(:last_modified, last_modified),
                        consecutive_failures = 0,
                        last_error = NULL,
                        status = CASE WHEN status = 'blocked' THEN status ELSE 'active' END,
                        updated_at = now()
                    WHERE id = :id
                    """
                ),
                {"id": source_id, "etag": etag, "last_modified": last_modified},
            )
        else:
            await session.execute(
                text(
                    """
                    UPDATE sources SET
                        last_fetched_at = now(),
                        consecutive_failures = consecutive_failures + 1,
                        last_error = :error,
                        status = CASE WHEN :blocked THEN 'blocked' ELSE status END,
                        updated_at = now()
                    WHERE id = :id
                    """
                ),
                {"id": source_id, "error": (error or "fetch failed")[:500], "blocked": blocked},
            )


async def set_fetch_state(source_id: str, state: dict[str, Any]) -> None:
    serialized = {key: value for key, value in state.items()}
    if "last_error" in serialized:
        serialized["last_error"] = str(serialized["last_error"])[:500]
    async with session_scope() as session:
        await session.execute(
            text(
                """
                UPDATE sources SET
                    etag = COALESCE(:etag, etag),
                    last_modified = COALESCE(:last_modified, last_modified),
                    last_fetched_at = now(),
                    last_success_at = CASE WHEN :success THEN now() ELSE last_success_at END,
                    consecutive_failures = CASE
                        WHEN :success THEN 0 ELSE consecutive_failures + 1 END,
                    last_error = :last_error,
                    status = CASE WHEN :blocked THEN 'blocked' ELSE status END,
                    updated_at = now()
                WHERE id = :id
                """
            ),
            {
                "id": source_id,
                "etag": state.get("etag"),
                "last_modified": state.get("last_modified"),
                "success": bool(state.get("success")),
                "last_error": serialized.get("last_error"),
                "blocked": bool(state.get("blocked")),
            },
        )


async def count_sources_by_language(industry_id: str) -> dict[str, int]:
    rows = await fetch_all(
        """
        SELECT language, COUNT(*) AS total
        FROM sources WHERE industry_id = :industry_id AND enabled = TRUE
        GROUP BY language
        """,
        {"industry_id": industry_id},
    )
    return {str(row["language"]): int(row["total"]) for row in rows}


def source_dto(source: Source, *, admin: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": source.id,
        "industry_id": source.industry_id,
        "name": source.name,
        "feed_url": source.feed_url,
        "language": source.language,
        "trust": source.trust,
        "enabled": source.enabled,
    }
    if admin:
        payload.update(
            {
                "allow_http": source.allow_http,
                "poll_interval_min": source.poll_interval_min,
                "terms_checked_at": source.terms_checked_at,
                "terms_url": source.terms_url,
                "status": source.status,
                "consecutive_failures": source.consecutive_failures,
                "last_error": source.last_error,
                "last_fetched_at": source.last_fetched_at,
                "last_success_at": source.last_success_at,
            }
        )
    return payload


def jsonb(value: Any) -> str:
    return json.dumps(value, default=str)
