from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from news_api.platform.db import fetch_all, fetch_one, session_scope

ARTICLE_COLUMNS = """
a.id, a.title, a.canonical_url, a.publisher, a.language, a.published_at,
a.status, a.hidden_reason, a.summary, a.excerpt, a.score, a.corroboration,
a.verification, a.is_seed, a.created_at, a.updated_at,
i.slug AS industry_slug
"""


async def admin_articles(
    *, industry_id: str | None, status: str | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    clauses = ["1 = 1"]
    params: dict[str, Any] = {"limit": min(limit, 200)}
    if industry_id:
        clauses.append("a.industry_id = CAST(:industry_id AS uuid)")
        params["industry_id"] = industry_id
    if status:
        clauses.append("a.status = :status")
        params["status"] = status
    return await fetch_all(
        f"""
        SELECT {ARTICLE_COLUMNS} FROM articles a
        JOIN industries i ON i.id = a.industry_id
        WHERE {' AND '.join(clauses)}
        ORDER BY a.published_at DESC LIMIT :limit
        """,
        params,
    )


async def get_article_admin(article_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        f"""
        SELECT {ARTICLE_COLUMNS} FROM articles a
        JOIN industries i ON i.id = a.industry_id
        WHERE a.id = CAST(:id AS uuid)
        """,
        {"id": article_id},
    )


async def set_article_status(article_id: str, status: str, reason: str | None) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text(
                """
                UPDATE articles SET status = :status, hidden_reason = :reason, updated_at = now()
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {"id": article_id, "status": status, "reason": reason},
        )
        return bool(getattr(result, "rowcount", 0))


async def list_pins(industry_id: str) -> list[dict[str, Any]]:
    return await fetch_all(
        """
        SELECT p.id, p.article_id, p.industry_id, p.position, p.weight, p.pin_expires_at,
               p.created_at, a.title, a.language, a.status
        FROM pins p JOIN articles a ON a.id = p.article_id
        WHERE p.industry_id = CAST(:industry_id AS uuid)
        ORDER BY p.position
        """,
        {"industry_id": industry_id},
    )


async def create_pin(
    *,
    article_id: str,
    industry_id: str,
    position: int,
    weight: float,
    expires_hours: int,
) -> dict[str, Any] | None:
    return await fetch_one(
        """
        INSERT INTO pins (article_id, industry_id, position, weight, pin_expires_at)
        VALUES (
            CAST(:article_id AS uuid), CAST(:industry_id AS uuid), :position, :weight,
            now() + make_interval(hours => :expires_hours)
        )
        ON CONFLICT (industry_id, position) DO NOTHING
        RETURNING id, article_id, industry_id, position, weight, pin_expires_at, created_at
        """,
        {
            "article_id": article_id,
            "industry_id": industry_id,
            "position": position,
            "weight": weight,
            "expires_hours": expires_hours,
        },
    )


async def delete_pin(pin_id: str) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text("DELETE FROM pins WHERE id = CAST(:id AS uuid)"), {"id": pin_id}
        )
        return bool(getattr(result, "rowcount", 0))


async def list_topics_admin(industry_id: str) -> list[dict[str, Any]]:
    return await fetch_all(
        """
        SELECT id, industry_id, slug, label, weight, keywords FROM topics
        WHERE industry_id = CAST(:industry_id AS uuid) ORDER BY weight DESC, slug
        """,
        {"industry_id": industry_id},
    )


async def create_topic(
    *,
    industry_id: str,
    slug: str,
    label: dict[str, str],
    weight: float,
    keywords: dict[str, list[str]],
) -> dict[str, Any] | None:
    return await fetch_one(
        """
        INSERT INTO topics (industry_id, slug, label, weight, keywords)
        VALUES (
            CAST(:industry_id AS uuid), :slug, CAST(:label AS jsonb), :weight,
            CAST(:keywords AS jsonb)
        )
        ON CONFLICT (industry_id, slug) DO NOTHING
        RETURNING id, industry_id, slug, label, weight, keywords
        """,
        {
            "industry_id": industry_id,
            "slug": slug,
            "label": json.dumps(label),
            "weight": weight,
            "keywords": json.dumps(keywords),
        },
    )


async def update_topic(topic_id: str, fields: dict[str, Any]) -> dict[str, Any] | None:
    assignments: list[str] = []
    params: dict[str, Any] = {"id": topic_id}
    for key in ("slug", "weight"):
        if key in fields:
            assignments.append(f"{key} = :{key}")
            params[key] = fields[key]
    if "label" in fields:
        assignments.append("label = CAST(:label AS jsonb)")
        params["label"] = json.dumps(fields["label"])
    if "keywords" in fields:
        assignments.append("keywords = CAST(:keywords AS jsonb)")
        params["keywords"] = json.dumps(fields["keywords"])
    if not assignments:
        return None
    assignments.append("updated_at = now()")
    return await fetch_one(
        f"""
        UPDATE topics SET {', '.join(assignments)} WHERE id = CAST(:id AS uuid)
        RETURNING id, industry_id, slug, label, weight, keywords
        """,
        params,
    )


async def delete_topic(topic_id: str) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text("DELETE FROM topics WHERE id = CAST(:id AS uuid)"), {"id": topic_id}
        )
        return bool(getattr(result, "rowcount", 0))


async def list_leads(
    *, industry_id: str | None, status: str | None, limit: int = 100
) -> list[dict[str, Any]]:
    clauses = ["1 = 1"]
    params: dict[str, Any] = {"limit": min(limit, 200)}
    if industry_id:
        clauses.append("l.industry_id = CAST(:industry_id AS uuid)")
        params["industry_id"] = industry_id
    if status:
        clauses.append("l.status = :status")
        params["status"] = status
    return await fetch_all(
        f"""
        SELECT l.id, l.industry_id, l.partner_id, l.kind, l.name, l.email, l.phone, l.company,
               l.message, l.locale, l.source_page, l.article_id, l.utm, l.consent_version,
               l.consent_at, l.country, l.session_hash, l.status, l.created_at, l.updated_at,
               i.slug AS industry_slug, p.name AS partner_name
        FROM leads l
        JOIN industries i ON i.id = l.industry_id
        LEFT JOIN partners p ON p.id = l.partner_id
        WHERE {' AND '.join(clauses)}
        ORDER BY l.created_at DESC LIMIT :limit
        """,
        params,
    )


async def get_lead(lead_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT l.*, i.slug AS industry_slug, p.name AS partner_name
        FROM leads l JOIN industries i ON i.id = l.industry_id
        LEFT JOIN partners p ON p.id = l.partner_id
        WHERE l.id = CAST(:id AS uuid)
        """,
        {"id": lead_id},
    )


async def add_lead_event(
    lead_id: str, *, actor: str, action: str, payload: dict[str, Any] | None = None
) -> None:
    async with session_scope() as session:
        await session.execute(
            text(
                """
                INSERT INTO lead_events (lead_id, actor, action, payload)
                VALUES (CAST(:lead_id AS uuid), :actor, :action, CAST(:payload AS jsonb))
                """
            ),
            {
                "lead_id": lead_id,
                "actor": actor,
                "action": action,
                "payload": json.dumps(payload or {}),
            },
        )


async def update_lead_status(lead_id: str, status: str) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text(
                """
                UPDATE leads SET status = :status, updated_at = now()
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {"id": lead_id, "status": status},
        )
        return bool(getattr(result, "rowcount", 0))


async def assign_lead(lead_id: str, partner_id: str | None) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text(
                """
                UPDATE leads SET partner_id = CAST(:partner_id AS uuid),
                    status = CASE WHEN :partner_id IS NULL THEN status ELSE 'routed' END,
                    updated_at = now()
                WHERE id = CAST(:id AS uuid)
                """
            ),
            {"id": lead_id, "partner_id": partner_id},
        )
        return bool(getattr(result, "rowcount", 0))


async def delete_lead(lead_id: str) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text("DELETE FROM leads WHERE id = CAST(:id AS uuid)"), {"id": lead_id}
        )
        return bool(getattr(result, "rowcount", 0))


async def list_partners(industry_id: str | None = None) -> list[dict[str, Any]]:
    guard = " WHERE p.industry_id = CAST(:industry_id AS uuid)" if industry_id else ""
    params: dict[str, Any] = {"industry_id": industry_id} if industry_id else {}
    return await fetch_all(
        f"""
        SELECT p.*, i.slug AS industry_slug FROM partners p
        JOIN industries i ON i.id = p.industry_id{guard}
        ORDER BY i.slug
        """,
        params,
    )


async def create_partner(
    *, industry_id: str, name: str, contact_email: str, regions: list[str]
) -> dict[str, Any] | None:
    return await fetch_one(
        """
        INSERT INTO partners (industry_id, name, contact_email, regions)
        VALUES (CAST(:industry_id AS uuid), :name, :contact_email, CAST(:regions AS jsonb))
        ON CONFLICT (industry_id) DO NOTHING
        RETURNING *
        """,
        {
            "industry_id": industry_id,
            "name": name,
            "contact_email": contact_email,
            "regions": json.dumps(regions),
        },
    )


async def update_partner(partner_id: str, fields: dict[str, Any]) -> dict[str, Any] | None:
    assignments: list[str] = []
    params: dict[str, Any] = {"id": partner_id}
    for key in ("name", "contact_email", "status", "weight"):
        if key in fields:
            assignments.append(f"{key} = :{key}")
            params[key] = fields[key]
    if "regions" in fields:
        assignments.append("regions = CAST(:regions AS jsonb)")
        params["regions"] = json.dumps(fields["regions"])
    if not assignments:
        return None
    assignments.append("updated_at = now()")
    return await fetch_one(
        f"UPDATE partners SET {', '.join(assignments)} WHERE id = CAST(:id AS uuid) RETURNING *",
        params,
    )


async def partner_contact_for(industry_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT id, name, contact_email FROM partners
        WHERE industry_id = CAST(:industry_id AS uuid) AND status = 'active'
        ORDER BY weight DESC LIMIT 1
        """,
        {"industry_id": industry_id},
    )


async def list_contacts(
    *, industry_id: str | None = None, status: str | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    clauses = ["1 = 1"]
    params: dict[str, Any] = {"limit": min(max(limit, 1), 200)}
    if industry_id:
        clauses.append("c.industry_id = CAST(:industry_id AS uuid)")
        params["industry_id"] = industry_id
    if status:
        clauses.append("c.status = :status")
        params["status"] = status
    return await fetch_all(
        f"""
        SELECT c.*, i.slug AS industry_slug
        FROM contact_messages c
        LEFT JOIN industries i ON i.id = c.industry_id
        WHERE {' AND '.join(clauses)}
        ORDER BY c.created_at DESC LIMIT :limit
        """,
        params,
    )


async def get_contact(contact_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT c.*, i.slug AS industry_slug
        FROM contact_messages c
        LEFT JOIN industries i ON i.id = c.industry_id
        WHERE c.id = CAST(:id AS uuid)
        """,
        {"id": contact_id},
    )


async def update_contact_status(contact_id: str, status: str) -> None:
    async with session_scope() as session:
        await session.execute(
            text("UPDATE contact_messages SET status = :status WHERE id = CAST(:id AS uuid)"),
            {"id": contact_id, "status": status},
        )


async def delete_contact(contact_id: str) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text("DELETE FROM contact_messages WHERE id = CAST(:id AS uuid)"),
            {"id": contact_id},
        )
        return int(getattr(result, "rowcount", 0) or 0) > 0
