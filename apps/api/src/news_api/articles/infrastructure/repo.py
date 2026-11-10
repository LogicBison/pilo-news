from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import text

from news_api.articles.domain.models import Candidate, Topic, topic_from_row
from news_api.platform.clock import utcnow
from news_api.platform.db import fetch_all, fetch_one, session_scope


async def list_topics(industry_id: str) -> list[Topic]:
    rows = await fetch_all(
        """
        SELECT id, slug, weight, keywords, label FROM topics
        WHERE industry_id = :industry_id ORDER BY weight DESC, slug
        """,
        {"industry_id": industry_id},
    )
    return [topic_from_row(row) for row in rows]


async def topics_with_counts(industry_id: str, language: str) -> list[dict[str, Any]]:
    rows = await fetch_all(
        """
        SELECT t.slug, t.label, t.weight, COUNT(a.id) AS total
        FROM topics t
        LEFT JOIN article_topics at ON at.topic_id = t.id
        LEFT JOIN articles a ON a.id = at.article_id
            AND a.status = 'published' AND a.language = :language
            AND a.published_at >= now() - make_interval(days => :days)
        WHERE t.industry_id = :industry_id
        GROUP BY t.id, t.slug, t.label, t.weight
        ORDER BY t.weight DESC, t.slug
        """,
        {"industry_id": industry_id, "language": language, "days": 7},
    )
    return rows


async def upsert_article(candidate: Candidate) -> tuple[str, bool]:
    row = await fetch_one(
        """
        INSERT INTO articles (
            id, industry_id, source_id, canonical_url, title, excerpt, publisher,
            language, published_at, fetched_at, score, corroboration,
            corroborating_sources, verification, status, is_seed
        ) VALUES (
            CAST(:id AS uuid), :industry_id, CAST(:source_id AS uuid), :canonical_url, :title,
            :excerpt, :publisher, :language, :published_at, now(), :score, :corroboration,
            CAST(:corroborating_sources AS jsonb), :verification, 'published', :is_seed
        )
        ON CONFLICT (canonical_url) DO UPDATE SET
            title = EXCLUDED.title,
            excerpt = EXCLUDED.excerpt,
            publisher = EXCLUDED.publisher,
            published_at = EXCLUDED.published_at,
            fetched_at = now(),
            score = EXCLUDED.score,
            corroboration = EXCLUDED.corroboration,
            corroborating_sources = EXCLUDED.corroborating_sources,
            verification = EXCLUDED.verification,
            is_seed = articles.is_seed OR EXCLUDED.is_seed,
            updated_at = now()
        RETURNING id, (xmax = 0) AS inserted
        """,
        {
            "id": candidate.article_id,
            "industry_id": candidate.industry_id,
            "source_id": candidate.source_id,
            "canonical_url": candidate.canonical_url,
            "title": candidate.title,
            "excerpt": candidate.excerpt,
            "publisher": candidate.publisher or candidate.source_name,
            "language": candidate.language,
            "published_at": candidate.published_at,
            "score": candidate.score,
            "corroboration": candidate.corroboration,
            "corroborating_sources": json.dumps(candidate.corroborating_sources),
            "verification": candidate.verification,
            "is_seed": candidate.is_seed,
        },
    )
    if not row:
        raise RuntimeError("article upsert returned no row")
    return str(row["id"]), bool(row["inserted"])


async def set_article_topics(article_id: str, topic_ids: list[str]) -> None:
    async with session_scope() as session:
        await session.execute(
            text("DELETE FROM article_topics WHERE article_id = CAST(:id AS uuid)"),
            {"id": article_id},
        )
        for topic_id in topic_ids:
            await session.execute(
                text(
                    """
                    INSERT INTO article_topics (article_id, topic_id)
                    VALUES (CAST(:article_id AS uuid), CAST(:topic_id AS uuid))
                    ON CONFLICT DO NOTHING
                    """
                ),
                {"article_id": article_id, "topic_id": topic_id},
            )


async def get_summary_state(article_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT summary, summary_source, summary_language, summary_version, title, excerpt, language
        FROM articles WHERE id = CAST(:id AS uuid)
        """,
        {"id": article_id},
    )


async def set_summary(
    article_id: str,
    summary: str,
    *,
    source: str,
    language: str,
    version: int = 1,
) -> None:
    async with session_scope() as session:
        await session.execute(
            text(
                """
                UPDATE articles SET
                    summary = :summary,
                    summary_source = :source,
                    summary_language = :language,
                    summary_version = :version,
                    updated_at = now()
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {
                "id": article_id,
                "summary": summary,
                "source": source,
                "language": language,
                "version": version,
            },
        )


async def clear_summaries(industry_id: str) -> int:
    async with session_scope() as session:
        result = await session.execute(
            text(
                """
                UPDATE articles SET summary = NULL, summary_source = NULL,
                    summary_language = NULL, summary_version = 1, updated_at = now()
                WHERE industry_id = CAST(:industry_id AS uuid)
                """
            ),
            {"industry_id": industry_id},
        )
        return int(getattr(result, "rowcount", 0) or 0)


async def create_run(
    industry_id: str | None,
    *,
    trigger: str,
    requested_by: str | None = None,
    status: str = "queued",
) -> str:
    row = await fetch_one(
        """
        INSERT INTO refresh_runs (industry_id, trigger, status, requested_by)
        VALUES (CAST(:industry_id AS uuid), :trigger, :status, :requested_by)
        RETURNING id
        """,
        {
            "industry_id": industry_id,
            "trigger": trigger,
            "status": status,
            "requested_by": requested_by,
        },
    )
    if not row:
        raise RuntimeError("refresh run insert failed")
    return str(row["id"])


async def update_run(
    run_id: str,
    *,
    status: str,
    stats: dict[str, Any] | None = None,
    finished: bool = True,
) -> None:
    async with session_scope() as session:
        await session.execute(
            text(
                """
                UPDATE refresh_runs SET
                    status = :status,
                    stats = CAST(:stats AS jsonb),
                    finished_at = CASE WHEN :finished THEN now() ELSE finished_at END
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {
                "id": run_id,
                "status": status,
                "stats": json.dumps(stats or {}),
                "finished": finished,
            },
        )


async def mark_run_running(run_id: str) -> None:
    async with session_scope() as session:
        await session.execute(
            text(
                """
                UPDATE refresh_runs SET status = 'running',
                    started_at = COALESCE(started_at, now())
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {"id": run_id},
        )


async def get_run(run_id: str) -> dict[str, Any] | None:
    row = await fetch_one(
        """
        SELECT r.*, i.slug AS industry_slug
        FROM refresh_runs r LEFT JOIN industries i ON i.id = r.industry_id
        WHERE r.id = CAST(:id AS uuid)
        """,
        {"id": run_id},
    )
    if not row:
        return None
    payload = dict(row)
    payload["stats"] = json.loads(row["stats"]) if isinstance(row["stats"], str) else row["stats"]
    return payload


async def list_runs_simple(limit: int = 10) -> list[dict[str, Any]]:
    rows = await fetch_all(
        """
        SELECT r.id, r.status, r.trigger, r.started_at, r.finished_at, r.stats,
               i.slug AS industry_slug
        FROM refresh_runs r LEFT JOIN industries i ON i.id = r.industry_id
        ORDER BY r.started_at DESC LIMIT :limit
        """,
        {"limit": max(1, min(limit, 100))},
    )
    result: list[dict[str, Any]] = []
    for row in rows:
        payload = dict(row)
        payload["run_id"] = str(payload.pop("id"))
        payload["stats"] = (
            json.loads(payload["stats"])
            if isinstance(payload.get("stats"), str)
            else payload.get("stats")
        )
        result.append(payload)
    return result


async def last_run(industry_id: str, trigger: str | None = None) -> dict[str, Any] | None:
    guard = " AND trigger = :trigger" if trigger else ""
    params: dict[str, Any] = {"industry_id": industry_id}
    if trigger:
        params["trigger"] = trigger
    return await fetch_one(
        f"""
        SELECT * FROM refresh_runs WHERE industry_id = CAST(:industry_id AS uuid){guard}
        ORDER BY started_at DESC LIMIT 1
        """,
        params,
    )


async def active_run(industry_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT * FROM refresh_runs
        WHERE industry_id = CAST(:industry_id AS uuid) AND status IN ('queued', 'running')
        ORDER BY started_at DESC LIMIT 1
        """,
        {"industry_id": industry_id},
    )


async def purge_old_content(
    *,
    article_days: int = 30,
    contact_days: int = 90,
    lead_months: int = 24,
    cta_days: int = 90,
) -> dict[str, int]:
    async with session_scope() as session:
        articles = await session.execute(
            text(
                """
                DELETE FROM articles a
                WHERE a.published_at < now() - make_interval(days => :days)
                  AND a.is_seed = FALSE
                  AND NOT EXISTS (SELECT 1 FROM pins p WHERE p.article_id = a.id)
                """
            ),
            {"days": article_days},
        )
        contacts = await session.execute(
            text(
                "DELETE FROM contact_messages "
                "WHERE created_at < now() - make_interval(days => :days)"
            ),
            {"days": contact_days},
        )
        spam_leads = await session.execute(
            text(
                """
                DELETE FROM leads
                WHERE status = 'spam' AND created_at < now() - make_interval(days => 90)
                """
            )
        )
        leads = await session.execute(
            text("DELETE FROM leads WHERE created_at < now() - make_interval(months => :months)"),
            {"months": lead_months},
        )
        cta = await session.execute(
            text("DELETE FROM cta_events WHERE created_at < now() - make_interval(days => :days)"),
            {"days": cta_days},
        )
    return {
        "articles": int(getattr(articles, "rowcount", 0) or 0),
        "contacts": int(getattr(contacts, "rowcount", 0) or 0),
        "leads": int(getattr(leads, "rowcount", 0) or 0)
        + int(getattr(spam_leads, "rowcount", 0) or 0),
        "cta_events": int(getattr(cta, "rowcount", 0) or 0),
    }


async def industry_article_counts(industry_id: str) -> dict[str, int]:
    rows = await fetch_all(
        """
        SELECT language, COUNT(*) AS total FROM articles
        WHERE industry_id = CAST(:industry_id AS uuid) AND status = 'published'
        GROUP BY language
        """,
        {"industry_id": industry_id},
    )
    return {str(row["language"]): int(row["total"]) for row in rows}


def iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def now_iso() -> str:
    return iso(utcnow()) or ""


async def record_outbound_click(article_id: str) -> str | None:
    """Count one reader leaving for the publisher, and return where they go.

    Aggregate only: no reader identifier, no IP, no user agent. A hidden or
    archived article is not a redirect target even if its id leaks.
    """
    row = await fetch_one(
        """
        UPDATE articles SET
            outbound_clicks = outbound_clicks + 1,
            updated_at = now()
        WHERE id = :id AND status = 'published'
        RETURNING canonical_url
        """,
        {"id": article_id},
    )
    return str(row["canonical_url"]) if row else None


async def recent_titles(industry_id: str | None = None, *, days: int = 30) -> list[str]:
    """Titles this desk already carries, for overlap scoring in discovery.

    Deliberately title-only: the question is "would this feed add stories we
    do not have", and a title match is a cheap upper bound on that.
    """
    where = [
        "status = 'published'",
        "created_at > now() - (CAST(:days AS integer) * interval '1 day')",
    ]
    params: dict[str, Any] = {"days": days}
    if industry_id:
        where.append("industry_id = :industry_id")
        params["industry_id"] = industry_id
    rows = await fetch_all(
        f"SELECT title FROM articles WHERE {' AND '.join(where)}",
        params,
    )
    return [str(row["title"]) for row in rows]


async def overlap_share(
    titles: list[str],
    industry_id: str | None = None,
    *,
    threshold: float = 0.45,
    days: int = 30,
) -> float:
    """Share of ``titles`` already carried by the desk, via pg_trgm.

    Trigram similarity is the database's own near-duplicate measure: it catches
    a reworded headline without loading every recent title into the process.
    The 0.45 default is looser than the in-process token threshold because the
    two scores are not comparable.
    """
    if not titles:
        return 0.0
    params: dict[str, Any] = {"titles": titles, "threshold": threshold, "days": days}
    clause = ""
    if industry_id:
        clause = "AND a.industry_id = CAST(:industry_id AS uuid)"
        params["industry_id"] = industry_id
    row = await fetch_one(
        f"""
        WITH candidate AS (SELECT unnest(CAST(:titles AS text[])) AS title)
        SELECT coalesce(
            count(*) FILTER (
                WHERE EXISTS (
                    SELECT 1 FROM articles a
                    WHERE a.status = 'published'
                      AND a.created_at > now() - (CAST(:days AS integer) * interval '1 day')
                      {clause}
                      AND similarity(a.title, candidate.title) > :threshold
                )
            )::float / NULLIF(count(*), 0),
            0
        ) AS share
        FROM candidate
        """,
        params,
    )
    return round(float(row["share"]), 3) if row else 0.0
