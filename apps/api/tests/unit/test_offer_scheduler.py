from __future__ import annotations

from datetime import UTC, datetime

import pytest

from news_api.articles.application import queue
from news_api.channels.domain.theme import Channel
from news_api.offers.application import scheduler
from news_api.offers.domain.models import OfferDefinition


def channel() -> Channel:
    return Channel(
        id="legal-id",
        slug="legal",
        code="LEGAL",
        name="Legal",
        base_name="Legal",
        tagline="",
        theme={},
        locales=["en"],
        disclaimers={},
        cta={"asset": "legal-regulatory-calendar"},
        timezone="UTC",
        retention_days=30,
        enabled=True,
        offers={"asset": True, "brief": False},
    )


def definition() -> OfferDefinition:
    return OfferDefinition(
        industry="legal",
        offer_slug="legal-regulatory-calendar",
        name="US Regulatory Calendar",
        adapter="federal_register",
        scope="US",
        cadence={"kind": "weekly", "weekday": 2},
        lookback_days=120,
        max_rows=12,
    )


@pytest.mark.asyncio
async def test_scheduler_enqueues_a_due_offer(monkeypatch) -> None:
    monkeypatch.setattr(scheduler, "load_definitions", lambda: {"legal": definition()})
    monkeypatch.setattr(scheduler, "get_channel", lambda *a, **k: _async(channel()))
    monkeypatch.setattr(scheduler, "get_issue", lambda **k: _async(None))
    monkeypatch.setattr(scheduler, "utcnow", lambda: datetime(2026, 11, 4, 12, tzinfo=UTC))

    created: list[dict] = []
    enqueued: list[dict] = []

    async def fake_upsert(**kwargs):
        created.append(kwargs)
        return {"id": "issue-1", **kwargs}

    async def fake_enqueue(**kwargs):
        enqueued.append(kwargs)
        return "1-0"

    monkeypatch.setattr(scheduler, "upsert_issue", fake_upsert)
    monkeypatch.setattr(queue, "enqueue_offer", fake_enqueue)

    count = await scheduler.offer_scheduler_tick()
    assert count == 1
    assert created[0]["issue_date"].isoformat() == "2026-11-04"
    assert enqueued[0]["offer"] == "legal-regulatory-calendar"


@pytest.mark.asyncio
async def test_scheduler_skips_an_existing_draft(monkeypatch) -> None:
    monkeypatch.setattr(scheduler, "load_definitions", lambda: {"legal": definition()})
    monkeypatch.setattr(scheduler, "get_channel", lambda *a, **k: _async(channel()))
    monkeypatch.setattr(
        scheduler,
        "get_issue",
        lambda **k: _async({"status": "draft", "generated_at": datetime.now(UTC)}),
    )
    monkeypatch.setattr(scheduler, "utcnow", lambda: datetime(2026, 11, 4, 12, tzinfo=UTC))
    count = await scheduler.offer_scheduler_tick()
    assert count == 0


async def _async(value):
    return value
