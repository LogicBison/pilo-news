"""Effective free-offer switches for a channel.

The console writes a four-key boolean map; readers get a normalized map even for
channels that predate the column. Defaults preserve the pre-console behaviour:
an asset channel offers the asset instead of the weekly brief.
"""

from __future__ import annotations

from typing import Any

from news_api.platform.jsons import as_dict

OFFER_KEYS: tuple[str, ...] = ("consultation", "brief", "question", "asset")


def _has_asset(cta: dict[str, Any]) -> bool:
    return bool(str(cta.get("asset") or "").strip())


def default_offers(cta: dict[str, Any] | None) -> dict[str, bool]:
    has_asset = _has_asset(as_dict(cta))
    return {
        "consultation": True,
        "brief": not has_asset,
        "question": True,
        "asset": has_asset,
    }


def resolve_offers(cta: dict[str, Any] | None, offers: Any) -> dict[str, bool]:
    """Return all four booleans, falling back per key to the legacy defaults."""
    defaults = default_offers(cta)
    stored = as_dict(offers)
    resolved: dict[str, bool] = {}
    for key in OFFER_KEYS:
        value = stored.get(key)
        resolved[key] = value if isinstance(value, bool) else defaults[key]
    # Defensive: a channel edited directly in the database must still render one
    # secondary rung. The admin API rejects this pair before it is written.
    if resolved["asset"] and not _has_asset(as_dict(cta)):
        resolved["asset"] = False
    if resolved["brief"] and resolved["asset"]:
        resolved["brief"] = False
    return resolved


def merge_offers(
    cta: dict[str, Any] | None, current: Any, patch: dict[str, bool]
) -> dict[str, bool]:
    """Merge a partial admin patch onto the effective map and write all four keys."""
    merged = {**resolve_offers(cta, current), **patch}
    return {key: bool(merged[key]) for key in OFFER_KEYS}


def validate_offers(cta: dict[str, Any] | None, offers: dict[str, bool]) -> list[str]:
    """Return human-readable problems; empty means the map is writable."""
    problems: list[str] = []
    unknown = sorted(set(offers) - set(OFFER_KEYS))
    if unknown:
        problems.append(f"unknown offer(s): {', '.join(unknown)}")
    for key in OFFER_KEYS:
        if key not in offers:
            problems.append(f"missing offer: {key}")
        elif not isinstance(offers[key], bool):
            problems.append(f"offer {key} must be true or false")
    if offers.get("brief") and offers.get("asset"):
        problems.append("brief and asset cannot both be enabled; choose one secondary offer")
    if offers.get("asset") and not _has_asset(as_dict(cta)):
        problems.append("asset offer requires a configured cta.asset for this channel")
    return problems
