"""What a source is worth, and when to propose retiring it.

Deliberately crude and explainable: a source earns its place by producing
stories the desk does not already have and by sending readers back. Clicks
weigh five times an item because they are the rarer signal.
"""

from __future__ import annotations

from typing import Any

CLICK_WEIGHT = 5.0
THIN_ITEMS = 5


def value_score(items_30d: int, clicks_30d: int) -> float:
    return round(items_30d + CLICK_WEIGHT * clicks_30d, 1)


def retirement_reason(row: dict[str, Any]) -> str | None:
    """A reason to propose retirement, or ``None`` to leave it alone.

    Never proposes a source that is already disabled, and never one that is
    producing readers: a low-item feed with clicks is doing its job.
    """
    if not row.get("enabled"):
        return None
    attempts = int(row.get("attempts_30d") or 0)
    items = int(row.get("items_30d") or 0)
    clicks = int(row.get("clicks_30d") or 0)
    if attempts >= 3 and items == 0:
        return f"no items from {attempts} attempts"
    if items < THIN_ITEMS and clicks == 0:
        return f"thin ({items} items) with no return clicks"
    return None
