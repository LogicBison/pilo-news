from __future__ import annotations

from datetime import datetime, timedelta

import structlog

from news_api.channels.infrastructure.repo import get_channel
from news_api.offers.application.config import load_definitions
from news_api.offers.domain.cadence import latest_due_date
from news_api.offers.infrastructure.repo import get_issue, mark_issue, upsert_issue
from news_api.platform.clock import utcnow

log = structlog.get_logger(__name__)

RETRY_AFTER = timedelta(hours=1)
STALE_AFTER = timedelta(minutes=15)


async def offer_scheduler_tick() -> int:
    """Enqueue draft generation for due offers. Never publishes."""
    today = utcnow().date()
    enqueued = 0
    for industry, definition in load_definitions().items():
        if not definition.enabled:
            continue
        channel = await get_channel(industry, enabled_only=False)
        if not channel or not channel.enabled:
            continue
        offers = channel.effective_offers
        if not offers.get("asset") or channel.cta.get("asset") != definition.offer_slug:
            continue
        target = latest_due_date(definition.cadence, today)
        if target is None:
            continue
        existing = await get_issue(
            industry_id=channel.id,
            offer_slug=definition.offer_slug,
            issue_date=target,
        )
        if existing:
            status = str(existing["status"])
            generated = existing.get("generated_at")
            age = utcnow() - generated if isinstance(generated, datetime) else None
            if status in ("draft", "empty", "published"):
                continue
            if status in ("queued", "building") and age is not None and age < STALE_AFTER:
                continue
            if status == "failed" and age is not None and age < RETRY_AFTER:
                continue
        issue = await upsert_issue(
            industry_id=channel.id,
            offer_slug=definition.offer_slug,
            issue_date=target,
            scope=definition.scope,
            status="queued",
            title=definition.name,
            standfirst="",
        )
        if not issue:
            continue
        from news_api.articles.application.queue import enqueue_offer

        try:
            await enqueue_offer(
                issue_id=str(issue["id"]),
                industry=industry,
                offer=definition.offer_slug,
                issue_date=target.isoformat(),
            )
        except Exception as exc:
            await mark_issue(
                issue_id=str(issue["id"]),
                status="failed",
                error=f"enqueue_failed: {type(exc).__name__}",
            )
            raise
        enqueued += 1
        log.info(
            "offer.scheduler.enqueued",
            industry=industry,
            offer=definition.offer_slug,
            issue_date=target.isoformat(),
        )
    return enqueued
