from __future__ import annotations

from typing import Any

UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")


def normalize_utm(value: Any) -> dict[str, str]:
    """Keep only the five campaign keys; drop unknown keys and long values."""
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, str] = {}
    for key in UTM_KEYS:
        item = value.get(key)
        if isinstance(item, str):
            cleaned = item.strip()[:120]
            if cleaned:
                normalized[key] = cleaned
    return normalized
