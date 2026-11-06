from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from urllib.parse import urlencode

from news_api.offers.domain.models import AdapterResult, RawRecord, parse_iso_date
from news_api.offers.infrastructure.fetch import fetch_json

SOURCE_URL = "https://www.federalregister.gov/api/v1/documents.json"
FIELDS = (
    "title",
    "publication_date",
    "effective_on",
    "comments_close_on",
    "html_url",
    "citation",
    "agencies",
    "type",
    "abstract",
)
WINDOW_BEFORE_DAYS = 0
WINDOW_AFTER_DAYS = 120
MAX_PAGES = 3


def _agencies(item: dict[str, Any]) -> str:
    names = [
        str(agency.get("name") or agency.get("raw_name") or "").strip()
        for agency in item.get("agencies") or []
        if isinstance(agency, dict)
    ]
    return ", ".join(name for name in names if name) or "Federal Register"


def _row_date(item: dict[str, Any], issue_date: date) -> tuple[date | None, str]:
    effective = parse_iso_date(str(item.get("effective_on") or ""))
    comments = parse_iso_date(str(item.get("comments_close_on") or ""))
    candidates: list[tuple[date, str]] = []
    if effective:
        candidates.append((effective, "Takes effect"))
    if comments:
        candidates.append((comments, "Comment window closes"))
    if not candidates:
        return None, ""
    window_start = issue_date - timedelta(days=WINDOW_BEFORE_DAYS)
    future = [pair for pair in candidates if pair[0] >= window_start]
    if not future:
        return None, ""
    return min(future, key=lambda pair: pair[0])


def parse_federal_register(payload: dict[str, Any], *, issue_date: date) -> AdapterResult:
    rows: list[RawRecord] = []
    window_end = issue_date + timedelta(days=WINDOW_AFTER_DAYS)
    seen: set[str] = set()
    for item in payload.get("results") or []:
        if not isinstance(item, dict):
            continue
        published = parse_iso_date(str(item.get("publication_date") or ""))
        if published and published > issue_date:
            continue
        chosen_date, action = _row_date(item, issue_date)
        if not chosen_date:
            continue
        if chosen_date > window_end:
            continue
        url = str(item.get("html_url") or "").strip()
        if not url.startswith(("http://", "https://")) or url in seen:
            continue
        seen.add(url)
        citation = str(item.get("citation") or "").strip()
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        rows.append(
            RawRecord(
                title=f"{citation} - {title}" if citation else title,
                date=chosen_date.isoformat(),
                jurisdiction="US",
                action=action,
                source_name=_agencies(item),
                source_url=url,
                summary=str(item.get("abstract") or "").strip(),
            )
        )
    rows.sort(key=lambda row: row.date)
    return AdapterResult(
        records=rows,
        source_version=str(payload.get("count") or ""),
        source_count=len(payload.get("results") or []),
    )


def build_url(*, since: date, until: date, agency_slugs: tuple[str, ...] = ()) -> str:
    params: list[tuple[str, str]] = [
        ("conditions[type][]", "RULE"),
        ("conditions[type][]", "PRORULE"),
        ("conditions[publication_date][gte]", since.isoformat()),
        ("conditions[publication_date][lte]", until.isoformat()),
        ("per_page", "100"),
        ("order", "newest"),
    ]
    params.extend(("conditions[agencies][]", slug) for slug in agency_slugs)
    params.extend(("fields[]", field) for field in FIELDS)
    return f"{SOURCE_URL}?{urlencode(params, doseq=True)}"


async def fetch_federal_register(
    *, since: date, issue_date: date, agency_slugs: tuple[str, ...] = ()
) -> AdapterResult:
    records: list[RawRecord] = []
    source_count = 0
    source_version = ""
    for page in range(1, MAX_PAGES + 1):
        url = build_url(since=since, until=issue_date, agency_slugs=agency_slugs)
        payload = await fetch_json(f"{url}&page={page}")
        parsed = parse_federal_register(payload, issue_date=issue_date)
        records.extend(parsed.records)
        source_count += parsed.source_count
        source_version = parsed.source_version or source_version
        if len(payload.get("results") or []) < 100:
            break
    deduped = {row.source_url: row for row in records}
    rows = sorted(deduped.values(), key=lambda row: row.date)
    return AdapterResult(records=rows, source_version=source_version, source_count=source_count)
