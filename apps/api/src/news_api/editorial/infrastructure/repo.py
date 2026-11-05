from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from news_api.platform.db import fetch_all, fetch_one, session_scope


async def find_api_key(key_hash: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT id, label, key_hash, key_prefix, scopes, rate_limit, enabled, last_used_at
        FROM api_keys WHERE key_hash = :key_hash
        """,
        {"key_hash": key_hash},
    )


async def touch_api_key(key_id: str) -> None:
    async with session_scope() as session:
        await session.execute(
            text("UPDATE api_keys SET last_used_at = now() WHERE id = CAST(:id AS uuid)"),
            {"id": key_id},
        )


async def list_api_keys() -> list[dict[str, Any]]:
    return await fetch_all(
        """
        SELECT id, label, key_prefix, scopes, rate_limit, enabled, last_used_at, created_at
        FROM api_keys ORDER BY created_at DESC
        """
    )


async def create_api_key(
    *, label: str, key_hash: str, key_prefix: str, scopes: list[str], rate_limit: int
) -> dict[str, Any] | None:
    return await fetch_one(
        """
        INSERT INTO api_keys (label, key_hash, key_prefix, scopes, rate_limit)
        VALUES (:label, :key_hash, :key_prefix, :scopes, :rate_limit)
        RETURNING id, label, key_prefix, scopes, rate_limit, enabled, created_at
        """,
        {
            "label": label,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "scopes": scopes,
            "rate_limit": rate_limit,
        },
    )


async def revoke_api_key(key_id: str) -> bool:
    async with session_scope() as session:
        result = await session.execute(
            text("UPDATE api_keys SET enabled = FALSE WHERE id = CAST(:id AS uuid)"),
            {"id": key_id},
        )
        return bool(getattr(result, "rowcount", 0))


async def count_active_keys() -> int:
    row = await fetch_one("SELECT COUNT(*) AS total FROM api_keys WHERE enabled = TRUE")
    return int(row["total"]) if row else 0


async def record_audit(
    *,
    actor: str,
    action: str,
    entity: str,
    entity_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    async with session_scope() as session:
        await session.execute(
            text(
                """
                INSERT INTO audit_events (actor, action, entity, entity_id, payload)
                VALUES (:actor, :action, :entity, :entity_id, CAST(:payload AS jsonb))
                """
            ),
            {
                "actor": actor,
                "action": action,
                "entity": entity,
                "entity_id": entity_id,
                "payload": json.dumps(payload or {}, default=str),
            },
        )


async def list_audit(action: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    guard = " WHERE action = :action" if action else ""
    params: dict[str, Any] = {"limit": min(limit, 200)}
    if action:
        params["action"] = action
    rows = await fetch_all(
        f"SELECT * FROM audit_events{guard} ORDER BY created_at DESC LIMIT :limit",
        params,
    )
    for row in rows:
        if isinstance(row.get("payload"), str):
            row["payload"] = json.loads(row["payload"])
    return rows
