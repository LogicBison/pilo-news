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
    # Permission record (source-availability SPEC). `permission_state` is the
    # robots verdict at the last check; the hash proves which robots text the
    # verdict came from. Credentials are never stored here: only the name of
    # the environment variable that holds them.
    permission_state: str = "unknown"
    robots_checked_at: str | None = None
    robots_hash: str | None = None
    robots_crawl_delay: int | None = None
    auth_type: str = "none"
    auth_header_name: str | None = None
    auth_secret_ref: str | None = None
    # Why we may republish a headline and an excerpt, and where the outreach
    # stands. `contacted_at` is set by the operator, not by a fetch.
    licence_type: str = "unknown"
    contacted_at: str | None = None
    outreach_note: str | None = None


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
        permission_state=str(row.get("permission_state") or "unknown"),
        robots_checked_at=str(row["robots_checked_at"]) if row.get("robots_checked_at") else None,
        robots_hash=row.get("robots_hash"),
        robots_crawl_delay=(
            int(row["robots_crawl_delay"]) if row.get("robots_crawl_delay") is not None else None
        ),
        auth_type=str(row.get("auth_type") or "none"),
        auth_header_name=row.get("auth_header_name"),
        auth_secret_ref=row.get("auth_secret_ref"),
        licence_type=str(row.get("licence_type") or "unknown"),
        contacted_at=str(row["contacted_at"]) if row.get("contacted_at") else None,
        outreach_note=row.get("outreach_note"),
    )
