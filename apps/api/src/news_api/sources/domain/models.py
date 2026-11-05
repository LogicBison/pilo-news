from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from news_api.platform.jsons import as_float


@dataclass(frozen=True)
class Source:
    id: str
    industry_id: str
    name: str
    feed_url: str
    language: str
    trust: float
    enabled: bool
    allow_http: bool
    poll_interval_min: int
    terms_checked_at: str | None
    terms_url: str | None
    etag: str | None
    last_modified: str | None
    last_fetched_at: str | None
    last_success_at: str | None
    status: str
    consecutive_failures: int
    last_error: str | None


def source_from_row(row: dict[str, Any]) -> Source:
    return Source(
        id=str(row["id"]),
        industry_id=str(row["industry_id"]),
        name=str(row["name"]),
        feed_url=str(row["feed_url"]),
        language=str(row["language"]),
        trust=as_float(row.get("trust"), 0.7),
        enabled=bool(row.get("enabled", True)),
        allow_http=bool(row.get("allow_http", False)),
        poll_interval_min=int(row.get("poll_interval_min") or 720),
        terms_checked_at=str(row["terms_checked_at"]) if row.get("terms_checked_at") else None,
        terms_url=row.get("terms_url"),
        etag=row.get("etag"),
        last_modified=row.get("last_modified"),
        last_fetched_at=str(row["last_fetched_at"]) if row.get("last_fetched_at") else None,
        last_success_at=str(row["last_success_at"]) if row.get("last_success_at") else None,
        status=str(row.get("status") or "active"),
        consecutive_failures=int(row.get("consecutive_failures") or 0),
        last_error=row.get("last_error"),
    )
