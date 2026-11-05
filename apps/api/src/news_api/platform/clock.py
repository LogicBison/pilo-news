from __future__ import annotations

from datetime import UTC, datetime, timedelta


def utcnow() -> datetime:
    """Single clock helper so domain code is testable."""
    return datetime.now(UTC)


def now_iso() -> str:
    return utcnow().isoformat().replace("+00:00", "Z")


def hours_ago(hours: float) -> datetime:
    return utcnow() - timedelta(hours=hours)


def days_ago(days: float) -> datetime:
    return utcnow() - timedelta(days=days)


def monthly_bucket() -> str:
    return utcnow().strftime("%Y%m")
