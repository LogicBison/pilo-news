from __future__ import annotations

from typing import Any

from sqlalchemy import text

from news_api.channels.domain.theme import Channel, channel_from_row
from news_api.platform.db import fetch_all, fetch_one, session_scope
from news_api.platform.jsons import as_dict

BASE_SELECT = """
SELECT i.*, COALESCE(l.name, i.name) AS display_name, COALESCE(l.tagline, '') AS tagline
FROM industries i
LEFT JOIN industry_locales l ON l.industry_id = i.id AND l.locale = :locale
"""


async def list_channels(locale: str = "en", *, enabled_only: bool = True) -> list[Channel]:
    where = " WHERE i.enabled = TRUE" if enabled_only else ""
    rows = await fetch_all(
        f"{BASE_SELECT}{where} ORDER BY i.sort_order ASC, i.slug ASC",
        {"locale": locale},
    )
    return [channel_from_row(row) for row in rows]


async def get_channel(
    slug: str, locale: str = "en", *, enabled_only: bool = True
) -> Channel | None:
    guard = " AND i.enabled = TRUE" if enabled_only else ""
    row = await fetch_one(
        f"{BASE_SELECT} WHERE i.slug = :slug{guard}",
        {"slug": slug, "locale": locale},
    )
    return channel_from_row(row) if row else None


async def get_channel_by_id(industry_id: str, locale: str = "en") -> Channel | None:
    row = await fetch_one(
        f"{BASE_SELECT} WHERE i.id = :industry_id",
        {"industry_id": industry_id, "locale": locale},
    )
    return channel_from_row(row) if row else None


async def channel_id_map() -> dict[str, str]:
    rows = await fetch_all("SELECT id, slug FROM industries")
    return {str(row["slug"]): str(row["id"]) for row in rows}


async def update_channel(
    slug: str,
    *,
    enabled: bool | None = None,
    theme: dict[str, Any] | None = None,
    disclaimers: dict[str, Any] | None = None,
    retention_days: int | None = None,
) -> bool:
    fields: list[str] = []
    params: dict[str, Any] = {"slug": slug}
    if enabled is not None:
        fields.append("enabled = :enabled")
        params["enabled"] = enabled
    if theme is not None:
        import json

        fields.append("theme = CAST(:theme AS jsonb)")
        params["theme"] = json.dumps(theme)
    if disclaimers is not None:
        import json

        fields.append("disclaimers = CAST(:disclaimers AS jsonb)")
        params["disclaimers"] = json.dumps(disclaimers)
    if retention_days is not None:
        fields.append("retention_days = :retention_days")
        params["retention_days"] = retention_days
    if not fields:
        return False
    fields.append("updated_at = now()")
    async with session_scope() as session:
        result = await session.execute(
            text(f"UPDATE industries SET {', '.join(fields)} WHERE slug = :slug"),
            params,
        )
        return bool(getattr(result, "rowcount", 0))


async def industry_settings(industry_id: str) -> dict[str, Any]:
    row = await fetch_one("SELECT * FROM industries WHERE id = :id", {"id": industry_id})
    if not row:
        return {}
    return {
        "slug": row["slug"],
        "retention_days": int(row["retention_days"]),
        "disclaimers": as_dict(row.get("disclaimers")),
        "cta": as_dict(row.get("cta")),
        "timezone": row["timezone"],
    }


async def create_channel(
    *,
    slug: str,
    code: str,
    name: str,
    theme: dict[str, Any],
    locales: dict[str, dict[str, str]],
    disclaimers: dict[str, str],
    cta: dict[str, Any],
    timezone: str,
    retention_days: int,
    sort_order: int,
    enabled: bool,
    topics: list[dict[str, Any]],
) -> Channel | None:
    import json

    async with session_scope() as session:
        row = await session.execute(
            text(
                """
                INSERT INTO industries (
                    slug, code, name, theme, locales, disclaimers, cta, timezone,
                    retention_days, sort_order, enabled
                ) VALUES (
                    :slug, :code, :name, CAST(:theme AS jsonb), :locales,
                    CAST(:disclaimers AS jsonb), CAST(:cta AS jsonb), :timezone,
                    :retention_days, :sort_order, :enabled
                )
                ON CONFLICT (slug) DO NOTHING
                RETURNING id
                """
            ),
            {
                "slug": slug,
                "code": code,
                "name": name,
                "theme": json.dumps(theme),
                "locales": list(locales.keys()) or ["en"],
                "disclaimers": json.dumps(disclaimers),
                "cta": json.dumps(cta),
                "timezone": timezone,
                "retention_days": retention_days,
                "sort_order": sort_order,
                "enabled": enabled,
            },
        )
        inserted = row.first()
        if not inserted:
            return None
        industry_id = str(inserted[0])
        for locale, copy in locales.items():
            await session.execute(
                text(
                    """
                    INSERT INTO industry_locales (industry_id, locale, name, tagline)
                    VALUES (CAST(:industry_id AS uuid), :locale, :name, :tagline)
                    """
                ),
                {
                    "industry_id": industry_id,
                    "locale": locale,
                    "name": copy.get("name", name),
                    "tagline": copy.get("tagline", ""),
                },
            )
        for topic in topics:
            await session.execute(
                text(
                    """
                    INSERT INTO topics (industry_id, slug, label, weight, keywords)
                    VALUES (
                        CAST(:industry_id AS uuid), :slug, CAST(:label AS jsonb), :weight,
                        CAST(:keywords AS jsonb)
                    )
                    ON CONFLICT (industry_id, slug) DO NOTHING
                    """
                ),
                {
                    "industry_id": industry_id,
                    "slug": topic["slug"],
                    "label": json.dumps(topic.get("label", {})),
                    "weight": float(topic.get("weight", 1.0)),
                    "keywords": json.dumps(topic.get("keywords", {})),
                },
            )
    return await get_channel(slug, enabled_only=False)
