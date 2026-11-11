"""Provider peak calendar.

DeepSeek bills model tokens at double rate during two weekday blocks, and at
half rate everywhere else. As of the pricing page checked on 2026-11-11 the
peak blocks are **01:00-04:00 and 06:00-10:00 UTC, Monday to Friday**, with
Chinese public holidays counted as off-peak all day. The older single
"08:30-16:30" window this module used to encode was wrong in both directions:
it bought peak tokens and blocked the cheapest afternoon hours.

The calendar is configuration, not a hard-coded clock, because the provider
publishes it and may move it. Everything here is a pure function so the rule
is testable without a network call or a frozen clock.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, time

HHMM_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
WINDOW_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$")


def parse_hhmm(value: str) -> time:
    match = HHMM_RE.match(value.strip())
    if not match:
        raise ValueError(f"invalid HH:MM value: {value!r}")
    return time(int(match.group(1)), int(match.group(2)))


def parse_peak_windows(value: str) -> list[tuple[time, time]]:
    """``"01:00-04:00,06:00-10:00"`` -> two half-open ranges.

    An empty string is a valid "no peak at all" calendar (every hour is cheap).
    """
    windows: list[tuple[time, time]] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        match = WINDOW_RE.match(item)
        if not match:
            raise ValueError(f"invalid peak window: {item!r}")
        start = time(int(match.group(1)), int(match.group(2)))
        end = time(int(match.group(3)), int(match.group(4)))
        if start == end:
            raise ValueError(f"empty peak window: {item!r}")
        windows.append((start, end))
    return windows


def parse_peak_days(value: str) -> frozenset[int]:
    """ISO weekdays (Monday = 1). Empty means every day is a peak day."""
    days: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            number = int(item)
        except ValueError as exc:
            raise ValueError(f"invalid peak day: {item!r}") from exc
        if not 1 <= number <= 7:
            raise ValueError(f"invalid peak day: {item!r}")
        days.add(number)
    return frozenset(days)


def parse_peak_holidays(value: str) -> frozenset[date]:
    """``"2026-10-01,2026-10-02"`` -> provider holidays (off-peak all day)."""
    holidays: set[date] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            holidays.add(date.fromisoformat(item))
        except ValueError as exc:
            raise ValueError(f"invalid holiday date: {item!r}") from exc
    return frozenset(holidays)


def is_peak(
    moment: datetime,
    *,
    windows: str,
    days: str,
    holidays: str = "",
) -> bool:
    """True when the call is billed at the peak rate."""
    utc = moment.astimezone(UTC)
    if utc.date() in parse_peak_holidays(holidays):
        return False
    if utc.isoweekday() not in parse_peak_days(days):
        return False
    current = utc.time().replace(tzinfo=None)
    for start, end in parse_peak_windows(windows):
        if start <= end:
            if start <= current < end:
                return True
        elif current >= start or current < end:
            # A block that crosses midnight, if the provider ever publishes one.
            return True
    return False


def is_offpeak(
    moment: datetime,
    *,
    windows: str,
    days: str,
    holidays: str = "",
) -> bool:
    return not is_peak(moment, windows=windows, days=days, holidays=holidays)
