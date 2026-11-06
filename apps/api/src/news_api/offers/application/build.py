from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import structlog

from news_api.channels.infrastructure.repo import get_channel
from news_api.offers.application.config import definition_for
from news_api.offers.application.draft import draft_rows
from news_api.offers.domain.cadence import latest_due_date
from news_api.offers.domain.models import OfferDefinition, RawRecord, parse_iso_date
from news_api.offers.infrastructure.adapters import fetch_records
from news_api.offers.infrastructure.repo import (
    issue_dto,
    last_issue_date,
    mark_issue,
    upsert_issue,
)
from news_api.platform.clock import utcnow
from news_api.platform.errors import NotFound, ValidationProblem
from news_api.platform.metrics import OFFER_ISSUES

log = structlog.get_logger(__name__)


def _clean_records(records: list[RawRecord], definition: OfferDefinition) -> list[RawRecord]:
    seen: set[str] = set()
    cleaned: list[RawRecord] = []
    for record in records:
        url = record.source_url.strip()
        if not url.startswith(("http://", "https://")) or url in seen:
            continue
        if not parse_iso_date(record.date):
            continue
        seen.add(url)
        cleaned.append(record)
    reverse = definition.adapter != "federal_register"
    cleaned.sort(key=lambda item: item.date, reverse=reverse)
    return cleaned[: definition.max_rows]


def _sources(records: list[RawRecord]) -> list[dict[str, str]]:
    seen: set[str] = set()
    sources: list[dict[str, str]] = []
    for record in records:
        if record.source_url in seen:
            continue
        seen.add(record.source_url)
        sources.append({"name": record.source_name, "url": record.source_url})
    return sources


def _standfirst(definition: OfferDefinition, issue_date: date, count: int) -> str:
    return (
        f"{count} dated changes. Scope: {definition.scope}. "
        f"Source checked {issue_date.isoformat()}."
    )


async def build_offer_issue(
    industry: str,
    *,
    offer_slug: str | None = None,
    issue_date: date | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    definition = definition_for(industry, offer_slug)
    if not definition:
        raise NotFound(f"No enabled offer definition for '{industry}'.")
    channel = await get_channel(industry, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{industry}'.")
    if not definition.enabled:
        raise ValidationProblem(f"Offer '{definition.offer_slug}' is disabled.")

    target = issue_date or latest_due_date(definition.cadence, utcnow().date())
    if target is None:
        raise ValidationProblem(f"Offer '{definition.offer_slug}' has an invalid cadence.")

    since = await last_issue_date(
        industry_id=channel.id, offer_slug=definition.offer_slug, before=target
    )
    if since is None:
        since = target - timedelta(days=definition.lookback_days)

    log.info(
        "offer.build.start",
        industry=industry,
        offer=definition.offer_slug,
        issue_date=target.isoformat(),
        since=since.isoformat(),
        adapter=definition.adapter,
        dry_run=dry_run,
    )

    issue_row = None
    if not dry_run:
        issue_row = await upsert_issue(
            industry_id=channel.id,
            offer_slug=definition.offer_slug,
            issue_date=target,
            scope=definition.scope,
            status="building",
            title=definition.name,
            standfirst="",
        )

    try:
        result = await fetch_records(definition, since=since, issue_date=target)
        records = _clean_records(result.records, definition)
        if not records:
            if not dry_run:
                assert issue_row is not None
                issue_row = await upsert_issue(
                    industry_id=channel.id,
                    offer_slug=definition.offer_slug,
                    issue_date=target,
                    scope=definition.scope,
                    status="empty",
                    title=definition.name,
                    standfirst=_standfirst(definition, target, 0),
                    sources=[],
                    source_version=result.source_version,
                )
            OFFER_ISSUES.labels(offer=definition.offer_slug, status="empty").inc()
            log.info(
                "offer.build.done",
                industry=industry,
                offer=definition.offer_slug,
                issue_date=target.isoformat(),
                status="empty",
                rows=0,
            )
            return {
                "industry": industry,
                "offer_slug": definition.offer_slug,
                "issue_date": target.isoformat(),
                "scope": definition.scope,
                "title": definition.name,
                "status": "empty",
                "rows": 0,
                "drafted_by": "none",
            }

        rows, drafted_by = await draft_rows(records, definition)
        if not rows:
            raise ValueError("draft returned no rows")

        standfirst = _standfirst(definition, target, len(rows))
        if dry_run:
            return {
                "industry": industry,
                "offer_slug": definition.offer_slug,
                "issue_date": target.isoformat(),
                "scope": definition.scope,
                "title": definition.name,
                "standfirst": standfirst,
                "status": "dry-run",
                "rows": len(rows),
                "drafted_by": drafted_by,
                "items": rows,
                "sources": _sources(records),
                "source_version": result.source_version,
            }

        assert issue_row is not None
        issue_row = await upsert_issue(
            industry_id=channel.id,
            offer_slug=definition.offer_slug,
            issue_date=target,
            scope=definition.scope,
            status="draft",
            title=definition.name,
            standfirst=standfirst,
            items=rows,
            sources=_sources(records),
            source_version=result.source_version,
        )
        OFFER_ISSUES.labels(offer=definition.offer_slug, status="draft").inc()
        log.info(
            "offer.build.done",
            industry=industry,
            offer=definition.offer_slug,
            issue_date=target.isoformat(),
            status="draft",
            rows=len(rows),
            drafted_by=drafted_by,
        )
        if not issue_row:
            raise RuntimeError("offer issue upsert returned no row")
        payload = issue_dto(issue_row)
        payload["industry"] = industry
        payload["drafted_by"] = drafted_by
        return payload
    except Exception as exc:
        if not dry_run and issue_row:
            await mark_issue(
                issue_id=str(issue_row["id"]),
                status="failed",
                error=f"{type(exc).__name__}: {exc}"[:300],
            )
        OFFER_ISSUES.labels(offer=definition.offer_slug, status="failed").inc()
        log.warning(
            "offer.build.failed",
            industry=industry,
            offer=definition.offer_slug,
            issue_date=target.isoformat(),
            error=type(exc).__name__,
        )
        raise
