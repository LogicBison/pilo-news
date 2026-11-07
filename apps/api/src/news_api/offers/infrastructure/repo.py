from __future__ import annotations

import json
from datetime import date
from typing import Any

from sqlalchemy import text

from news_api.platform.db import fetch_all, fetch_one, session_scope


def issue_dto(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "industry": row.get("industry_slug"),
        "offer_slug": row["offer_slug"],
        "issue_date": row["issue_date"].isoformat()
        if hasattr(row["issue_date"], "isoformat")
        else str(row["issue_date"]),
        "scope": row["scope"],
        "status": row["status"],
        "title": row["title"],
        "standfirst": row.get("standfirst") or "",
        "items": row.get("items") or [],
        "sources": row.get("sources") or [],
        "source_version": row.get("source_version"),
        "reviewer": row.get("reviewer"),
        "error": row.get("error"),
        "generated_at": row.get("generated_at"),
        "published_at": row.get("published_at"),
    }


async def upsert_issue(
    *,
    industry_id: str,
    offer_slug: str,
    issue_date: date,
    scope: str,
    status: str,
    title: str,
    standfirst: str = "",
    items: list[dict[str, Any]] | None = None,
    sources: list[dict[str, Any]] | None = None,
    source_version: str | None = None,
    error: str | None = None,
) -> dict[str, Any] | None:
    row = await fetch_one(
        """
        INSERT INTO offer_issues (
            industry_id, offer_slug, issue_date, scope, status, title, standfirst,
            items, sources, source_version, error
        ) VALUES (
            CAST(:industry_id AS uuid), :offer_slug, :issue_date, :scope, :status,
            :title, :standfirst, CAST(:items AS jsonb), CAST(:sources AS jsonb),
            :source_version, :error
        )
        ON CONFLICT (industry_id, offer_slug, issue_date) DO UPDATE SET
            scope = EXCLUDED.scope,
            status = EXCLUDED.status,
            title = EXCLUDED.title,
            standfirst = EXCLUDED.standfirst,
            items = EXCLUDED.items,
            sources = EXCLUDED.sources,
            source_version = EXCLUDED.source_version,
            reviewer = CASE WHEN EXCLUDED.status = 'draft' THEN NULL ELSE offer_issues.reviewer END,
            error = EXCLUDED.error,
            generated_at = now()
        RETURNING *
        """,
        {
            "industry_id": industry_id,
            "offer_slug": offer_slug,
            "issue_date": issue_date,
            "scope": scope,
            "status": status,
            "title": title,
            "standfirst": standfirst,
            "items": json.dumps(items or []),
            "sources": json.dumps(sources or []),
            "source_version": source_version,
            "error": error,
        },
    )
    return row


async def get_issue(
    *, industry_id: str, offer_slug: str, issue_date: date
) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT * FROM offer_issues
        WHERE industry_id = CAST(:industry_id AS uuid)
          AND offer_slug = :offer_slug AND issue_date = :issue_date
        """,
        {
            "industry_id": industry_id,
            "offer_slug": offer_slug,
            "issue_date": issue_date,
        },
    )


async def get_issue_by_id(issue_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT oi.*, i.slug AS industry_slug FROM offer_issues oi
        JOIN industries i ON i.id = oi.industry_id
        WHERE oi.id = CAST(:id AS uuid)
        """,
        {"id": issue_id},
    )


async def list_issues(
    *, industry_id: str | None = None, status: str | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: dict[str, Any] = {"limit": min(max(limit, 1), 100)}
    if industry_id:
        clauses.append("oi.industry_id = CAST(:industry_id AS uuid)")
        params["industry_id"] = industry_id
    if status:
        clauses.append("oi.status = :status")
        params["status"] = status
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = await fetch_all(
        f"""
        SELECT oi.*, i.slug AS industry_slug FROM offer_issues oi
        JOIN industries i ON i.id = oi.industry_id
        {where}
        ORDER BY oi.issue_date DESC, oi.generated_at DESC
        LIMIT :limit
        """,
        params,
    )
    return rows


async def last_issue_date(*, industry_id: str, offer_slug: str, before: date) -> date | None:
    row = await fetch_one(
        """
        SELECT MAX(issue_date) AS last_date FROM offer_issues
        WHERE industry_id = CAST(:industry_id AS uuid)
          AND offer_slug = :offer_slug AND issue_date < :before
          AND status IN ('draft', 'empty', 'published')
        """,
        {"industry_id": industry_id, "offer_slug": offer_slug, "before": before},
    )
    return row["last_date"] if row and row.get("last_date") else None


async def mark_issue(*, issue_id: str, status: str, error: str | None = None) -> None:
    async with session_scope() as session:
        await session.execute(
            text(
                """
                UPDATE offer_issues SET status = :status, error = :error,
                    generated_at = now()
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {"id": issue_id, "status": status, "error": error},
        )


async def list_published(industry_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
    return await fetch_all(
        """
        SELECT * FROM offer_issues
        WHERE industry_id = CAST(:industry_id AS uuid) AND status = 'published'
        ORDER BY issue_date DESC
        LIMIT :limit
        """,
        {"industry_id": industry_id, "limit": min(max(limit, 1), 100)},
    )


async def get_published(industry_id: str, issue_date: date) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT * FROM offer_issues
        WHERE industry_id = CAST(:industry_id AS uuid)
          AND issue_date = :issue_date AND status = 'published'
        """,
        {"industry_id": industry_id, "issue_date": issue_date},
    )


async def publish_issue(issue_id: str, reviewer: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        UPDATE offer_issues SET
            status = 'published',
            reviewer = :reviewer,
            published_at = now(),
            error = NULL
        WHERE id = CAST(:id AS uuid)
          AND status = 'draft'
          AND jsonb_array_length(items) > 0
        RETURNING *
        """,
        {"id": issue_id, "reviewer": reviewer},
    )


async def unpublish_issue(issue_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        UPDATE offer_issues SET
            status = 'draft',
            reviewer = NULL,
            published_at = NULL
        WHERE id = CAST(:id AS uuid) AND status = 'published'
        RETURNING *
        """,
        {"id": issue_id},
    )
