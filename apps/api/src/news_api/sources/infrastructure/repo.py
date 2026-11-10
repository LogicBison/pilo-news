from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from news_api.platform.db import fetch_all, fetch_one, session_scope
from news_api.sources.domain.models import Source, source_from_row

COLUMNS = """
id, industry_id, name, feed_url, language, trust, enabled, allow_http, poll_interval_min,
terms_checked_at, terms_url, etag, last_modified, last_fetched_at, last_success_at,
status, consecutive_failures, last_error, permission_state, robots_checked_at,
robots_hash, robots_crawl_delay, auth_type, auth_header_name, auth_secret_ref,
licence_type, contacted_at, outreach_note
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
    permission_state: str = "unknown",
    auth_type: str = "none",
    auth_header_name: str | None = None,
    auth_secret_ref: str | None = None,
    licence_type: str = "unknown",
) -> Source | None:
    row = await fetch_one(
        f"""
        INSERT INTO sources (
            industry_id, name, feed_url, language, trust, enabled, allow_http,
            poll_interval_min, terms_checked_at, terms_url, permission_state,
            auth_type, auth_header_name, auth_secret_ref, licence_type
        ) VALUES (
            :industry_id, :name, :feed_url, :language, :trust, :enabled, :allow_http,
            :poll_interval_min, :terms_checked_at, :terms_url, :permission_state,
            :auth_type, :auth_header_name, :auth_secret_ref, :licence_type
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
            "permission_state": permission_state,
            "auth_type": auth_type,
            "auth_header_name": auth_header_name,
            "auth_secret_ref": auth_secret_ref,
            "licence_type": licence_type,
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
        "auth_type",
        "auth_header_name",
        "auth_secret_ref",
        "licence_type",
        "outreach_note",
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


async def set_permission(
    source_id: str,
    *,
    state: str,
    checked_at: Any,
    robots_hash: str | None,
    crawl_delay: int | None,
) -> None:
    """Record the robots verdict that let (or stopped) the last check.

    Written by `verify-sources`, not by the fetch path: the runner is where an
    operator asks "may we still read this", and it costs one write per run
    instead of one per fetch.
    """
    async with session_scope() as session:
        await session.execute(
            text(
                """
                UPDATE sources SET
                    permission_state = :state,
                    robots_checked_at = :checked_at,
                    robots_hash = :robots_hash,
                    robots_crawl_delay = :crawl_delay,
                    updated_at = now()
                WHERE id = :id
                """
            ),
            {
                "id": source_id,
                "state": state,
                "checked_at": checked_at,
                "robots_hash": robots_hash,
                "crawl_delay": crawl_delay,
            },
        )


async def set_outreach(source_id: str, *, note: str | None) -> Source | None:
    """Record that a publisher was contacted, and what came of it."""
    row = await fetch_one(
        f"""
        UPDATE sources SET
            contacted_at = now(),
            outreach_note = :note,
            updated_at = now()
        WHERE id = :id
        RETURNING {COLUMNS}
        """,
        {"id": source_id, "note": (note or "")[:2000]},
    )
    return source_from_row(row) if row else None


async def source_health(industry_id: str | None = None) -> list[dict[str, Any]]:
    """Per-source output, attempts and return traffic over the last 30 days.

    Articles show what a feed produced; fetch stats show whether it answered.
    A source with attempts and no items is not "quiet", it is failing.
    """
    where = "WHERE s.industry_id = :industry_id" if industry_id else ""
    rows = await fetch_all(
        f"""
        SELECT s.id, s.name, s.language, s.licence_type, s.enabled, s.status,
               s.last_success_at, s.consecutive_failures, s.permission_state,
               count(a.id) FILTER (WHERE a.created_at > now() - interval '7 days') AS items_7d,
               count(a.id) FILTER (WHERE a.created_at > now() - interval '30 days') AS items_30d,
               coalesce(
                   sum(a.outbound_clicks) FILTER (
                       WHERE a.created_at > now() - interval '30 days'
                   ), 0
               ) AS clicks_30d,
               coalesce(sum(f.attempts), 0) AS attempts_30d,
               coalesce(sum(f.ok), 0) AS ok_30d,
               coalesce(sum(f.blocked), 0) AS blocked_30d,
               coalesce(sum(f.denied), 0) AS denied_30d,
               coalesce(
                   sum(f.duration_ms) FILTER (WHERE f.ok > 0), 0
               ) AS ok_duration_ms_30d
        FROM sources s
        LEFT JOIN articles a ON a.source_id = s.id
        LEFT JOIN source_fetch_stats f
            ON f.source_id = s.id AND f.day > CURRENT_DATE - 30
        {where}
        GROUP BY s.id
        ORDER BY items_30d DESC, s.name
        """,
        {"industry_id": industry_id} if industry_id else {},
    )
    out: list[dict[str, Any]] = []
    for row in rows:
        record = dict(row)
        for key in ("items_7d", "items_30d", "clicks_30d", "attempts_30d", "ok_30d"):
            record[key] = int(record.get(key) or 0)
        for key in ("blocked_30d", "denied_30d", "ok_duration_ms_30d"):
            record[key] = int(record.get(key) or 0)
        attempts = int(record["attempts_30d"])
        record["success_rate_30d"] = (
            round(int(record["ok_30d"]) / attempts, 3) if attempts else None
        )
        record["avg_ms_30d"] = (
            round(int(record["ok_duration_ms_30d"]) / int(record["ok_30d"]))
            if record["ok_30d"]
            else None
        )
        out.append(record)
    return out


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
                # R10: the admin view names the streak the way the fetcher does.
                "fail_streak": source.consecutive_failures,
                "last_error": source.last_error,
                "last_fetched_at": source.last_fetched_at,
                "last_success_at": source.last_success_at,
                "permission_state": source.permission_state,
                "robots_checked_at": source.robots_checked_at,
                "robots_hash": source.robots_hash,
                "robots_crawl_delay": source.robots_crawl_delay,
                "auth_type": source.auth_type,
                "auth_header_name": source.auth_header_name,
                # The reference, not the secret: an env var name an operator
                # can check exists, with no credential in the API response.
                "auth_secret_ref": source.auth_secret_ref,
                "licence_type": source.licence_type,
                "contacted_at": source.contacted_at,
                "outreach_note": source.outreach_note,
            }
        )
    return payload


def jsonb(value: Any) -> str:
    return json.dumps(value, default=str)


async def record_fetch_stat(
    source_id: str,
    *,
    status: str,
    items: int,
    duration_ms: int,
) -> None:
    """One day-level row per source, folded in after every fetch.

    A failed fetch has no articles, so article counts alone cannot separate a
    refused feed from a quiet one. This is the missing half of source health.
    """
    ok = 1 if status in ("ok", "http_304") else 0
    blocked = 1 if status in ("blocked", "rate_limited", "robots_disallowed", "challenge") else 0
    denied = 1 if status == "denied" else 0
    async with session_scope() as session:
        await session.execute(
            text(
                """
                INSERT INTO source_fetch_stats
                    (source_id, day, attempts, ok, blocked, denied, items, duration_ms)
                VALUES (:source_id, CURRENT_DATE, 1, :ok, :blocked, :denied, :items, :duration_ms)
                ON CONFLICT (source_id, day) DO UPDATE SET
                    attempts = source_fetch_stats.attempts + 1,
                    ok = source_fetch_stats.ok + EXCLUDED.ok,
                    blocked = source_fetch_stats.blocked + EXCLUDED.blocked,
                    denied = source_fetch_stats.denied + EXCLUDED.denied,
                    items = source_fetch_stats.items + EXCLUDED.items,
                    duration_ms = source_fetch_stats.duration_ms + EXCLUDED.duration_ms
                """
            ),
            {
                "source_id": source_id,
                "ok": ok,
                "blocked": blocked,
                "denied": denied,
                "items": max(items, 0),
                "duration_ms": max(duration_ms, 0),
            },
        )


async def upsert_candidates(rows: list[dict[str, Any]]) -> int:
    """Persist discovery findings without overwriting an operator decision."""
    saved = 0
    async with session_scope() as session:
        for row in rows:
            result = await session.execute(
                text(
                    """
                    INSERT INTO source_candidates
                        (feed_url, name, industry_id, language, grade, overlap, verdict)
                    VALUES
                        (:feed_url, :name, :industry_id, :language, :grade, :overlap, :verdict)
                    ON CONFLICT (feed_url) DO UPDATE SET
                        name = EXCLUDED.name,
                        industry_id = COALESCE(EXCLUDED.industry_id, source_candidates.industry_id),
                        language = EXCLUDED.language,
                        grade = EXCLUDED.grade,
                        overlap = EXCLUDED.overlap,
                        verdict = EXCLUDED.verdict,
                        discovered_at = now()
                    WHERE source_candidates.status IN ('new', 'shortlisted')
                    RETURNING id
                    """
                ),
                row,
            )
            saved += 1 if result.first() else 0
    return saved


async def list_candidates(status: str | None = None, *, limit: int = 100) -> list[dict[str, Any]]:
    where = "WHERE status = :status" if status else ""
    rows = await fetch_all(
        f"""
        SELECT id, feed_url, name, language, grade, overlap, verdict, status, note,
               discovered_at, decided_at
        FROM source_candidates
        {where}
        ORDER BY discovered_at DESC
        LIMIT :limit
        """,
        {"status": status, "limit": limit} if status else {"limit": limit},
    )
    return [dict(row) for row in rows]


async def decide_candidate(
    candidate_id: str, *, status: str, note: str = ""
) -> dict[str, Any] | None:
    if status not in ("new", "shortlisted", "accepted", "dismissed"):
        raise ValueError(f"unknown candidate status: {status}")
    row = await fetch_one(
        """
        UPDATE source_candidates SET
            status = :status,
            note = CASE WHEN :note = '' THEN note ELSE :note END,
            decided_at = now()
        WHERE id = :id
        RETURNING id, feed_url, name, language, grade, overlap, verdict, status, note
        """,
        {"id": candidate_id, "status": status, "note": note},
    )
    return dict(row) if row else None


async def candidate_snippet(candidate_id: str) -> dict[str, Any] | None:
    """The profile row for an accepted candidate."""
    row = await fetch_one(
        """
        SELECT feed_url, name, language
        FROM source_candidates
        WHERE id = :id AND status = 'accepted'
        """,
        {"id": candidate_id},
    )
    if not row:
        return None
    return {
        "name": row["name"] or str(row["feed_url"]),
        "feed_url": str(row["feed_url"]),
        "language": str(row["language"] or "en"),
        "trust": 0.8,
        "enabled": True,
        "allow_http": False,
        "poll_interval_min": 720,
        "terms_url": None,
        "licence_type": "unknown",
    }
