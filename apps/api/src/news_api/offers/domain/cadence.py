from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Any


def _nth_weekday(year: int, month: int, weekday: int, nth: int) -> date:
    """Return the nth (1-based) weekday in a month. weekday: Monday=0."""
    first_weekday, days = calendar.monthrange(year, month)
    offset = (weekday - first_weekday) % 7
    day = 1 + offset + (nth - 1) * 7
    if day > days:
        # clamp to the last occurrence; callers use nth=1..4 in practice
        day -= 7
    return date(year, month, day)


def _previous_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def latest_due_date(cadence: dict[str, Any], today: date) -> date | None:
    """The most recent scheduled date at or before today, or None if malformed."""
    kind = str(cadence.get("kind", "")).lower()
    if kind == "weekly":
        try:
            weekday = int(cadence["weekday"])
        except (KeyError, TypeError, ValueError):
            return None
        if not 0 <= weekday <= 6:
            return None
        return today - timedelta(days=(today.weekday() - weekday) % 7)

    if kind == "monthly":
        if "day" in cadence:
            try:
                day = int(cadence["day"])
            except (TypeError, ValueError):
                return None
            if not 1 <= day <= 31:
                return None
            days_in_month = calendar.monthrange(today.year, today.month)[1]
            candidate = date(today.year, today.month, min(day, days_in_month))
            if candidate <= today:
                return candidate
            year, month = _previous_month(today.year, today.month)
            return date(year, month, min(day, calendar.monthrange(year, month)[1]))

        try:
            weekday = int(cadence["weekday"])
            nth = int(cadence.get("nth", 1))
        except (KeyError, TypeError, ValueError):
            return None
        if not 0 <= weekday <= 6 or not 1 <= nth <= 5:
            return None
        candidate = _nth_weekday(today.year, today.month, weekday, nth)
        if candidate <= today:
            return candidate
        year, month = _previous_month(today.year, today.month)
        return _nth_weekday(year, month, weekday, nth)

    return None


def cadence_days(cadence: dict[str, Any]) -> int:
    return 7 if str(cadence.get("kind", "")).lower() == "weekly" else 31
