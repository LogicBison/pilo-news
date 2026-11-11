"""Runtime overrides for the AI cost controls.

`.env.<env>` is the deployment's default; the admin console is the operator's
live knob. A row in ``platform_settings`` wins over the environment for the
keys listed in :data:`OVERRIDABLE`, without a restart: each process caches the
row for :data:`CACHE_SECONDS`, the writing process invalidates its own cache
immediately, and every other process follows within the TTL.

Only cost-shaped, non-secret keys qualify. The API key, the base URL and the
model stay environment-only: one is a secret, the others are a deployment
decision that should show up in a deploy, not in a web form.
"""

from __future__ import annotations

import json
import time
from typing import Any

import structlog

from news_api.platform.db import fetch_one, session_scope
from news_api.platform.jsons import as_dict

log = structlog.get_logger(__name__)

SETTINGS_KEY = "ai"
CACHE_SECONDS = 5.0

OVERRIDABLE: tuple[str, ...] = (
    "ai_enabled",
    "ai_monthly_budget_usd",
    "ai_max_items_per_run",
    "ai_offpeak_only",
    "ai_peak_windows",
    "ai_peak_days",
    "ai_peak_holidays",
)

_cache: dict[str, Any] = {}
_cached_at = 0.0


def invalidate() -> None:
    """Forget the cached row (the writer calls this; others wait for the TTL)."""
    global _cached_at
    _cached_at = 0.0


async def load() -> dict[str, Any]:
    """Overrides currently in force. A read failure keeps the last known good."""
    global _cache, _cached_at
    now = time.monotonic()
    if _cached_at and now - _cached_at < CACHE_SECONDS:
        return _cache
    try:
        row = await fetch_one(
            "SELECT value FROM platform_settings WHERE key = :key", {"key": SETTINGS_KEY}
        )
    except Exception as exc:  # pragma: no cover - database failure path
        log.warning("settings.overrides_unreadable", error=type(exc).__name__)
        _cached_at = now
        return _cache
    value = as_dict(row.get("value")) if row else {}
    _cache = {key: value[key] for key in OVERRIDABLE if key in value}
    _cached_at = now
    return _cache


async def save(patch: dict[str, Any], *, updated_by: str | None) -> dict[str, Any]:
    """Merge ``patch`` into the stored row and return the new overrides.

    A ``None`` value removes that override, so the field falls back to `.env`
    without clearing the rest of the panel.
    """
    current = dict(await load())
    for key, value in patch.items():
        if key not in OVERRIDABLE:
            continue
        if value is None:
            current.pop(key, None)
        else:
            current[key] = value
    async with session_scope() as session:
        from sqlalchemy import text

        await session.execute(
            text(
                """
                INSERT INTO platform_settings (key, value, updated_at, updated_by)
                VALUES (:key, CAST(:value AS jsonb), now(), :updated_by)
                ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value,
                    updated_at = now(),
                    updated_by = EXCLUDED.updated_by
                """
            ),
            {
                "key": SETTINGS_KEY,
                "value": json.dumps(current),
                "updated_by": updated_by,
            },
        )
    invalidate()
    return current


async def clear(*, updated_by: str | None) -> dict[str, Any]:
    """Drop every override: the panel returns to the `.env` values."""
    return await save({key: None for key in OVERRIDABLE}, updated_by=updated_by)


async def stored() -> dict[str, Any]:
    """The row as written, bypassing the process cache (used by the admin read)."""
    try:
        row = await fetch_one(
            "SELECT value, updated_at, updated_by FROM platform_settings WHERE key = :key",
            {"key": SETTINGS_KEY},
        )
    except Exception:  # pragma: no cover
        return {}
    if not row:
        return {}
    value = as_dict(row.get("value"))
    return {
        "values": {key: value[key] for key in OVERRIDABLE if key in value},
        "updated_at": row.get("updated_at"),
        "updated_by": row.get("updated_by"),
    }
