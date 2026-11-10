"""Off-peak windows for provider calls.

DeepSeek prices by UTC clock: the discounted windows sit outside 08:30-16:30
UTC. This module answers one question — "is now inside the cheap window" — as a
pure function, so the rule is testable without a clock or a network call.

The window may cross midnight (16:30 → 08:30), which is the normal case.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, time

HHMM_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def parse_hhmm(value: str) -> time:
    match = HHMM_RE.match(value.strip())
    if not match:
        raise ValueError(f"invalid HH:MM value: {value!r}")
    return time(int(match.group(1)), int(match.group(2)))


def in_window(moment: datetime, start: str, end: str) -> bool:
    """True when ``moment`` is inside ``[start, end)`` on the UTC clock.

    ``start == end`` is treated as empty rather than all-day: a misconfigured
    window should spend nothing, not everything.
    """
    start_t = parse_hhmm(start)
    end_t = parse_hhmm(end)
    current = moment.astimezone(UTC).time().replace(tzinfo=None)
    if start_t == end_t:
        return False
    if start_t < end_t:
        return start_t <= current < end_t
    return current >= start_t or current < end_t
