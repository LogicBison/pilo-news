from __future__ import annotations

from datetime import date

import pytest

from news_api.channels.infrastructure.repo import get_channel
from news_api.offers.application import build as build_module
from news_api.offers.application.build import build_offer_issue
from news_api.offers.domain.models import AdapterResult, RawRecord
from news_api.offers.infrastructure.repo import get_issue


def record(**overrides: str) -> RawRecord:
    values = {
        "title": "US rule takes effect",
        "date": "2026-12-01",
        "jurisdiction": "US",
        "action": "Takes effect",
        "source_name": "Federal Register",
        "source_url": "https://www.federalregister.gov/documents/2026/11/01/a",
        "summary": "A filing change.",
    }
    values.update(overrides)
    return RawRecord(**values)


@pytest.mark.asyncio
async def test_build_writes_a_draft_and_is_idempotent(clean_db, monkeypatch) -> None:
    async def fake_fetch(*_args, **_kwargs) -> AdapterResult:
        return AdapterResult(records=[record()], source_version="test-1", source_count=1)

    monkeypatch.setattr(build_module, "fetch_records", fake_fetch)
    first = await build_offer_issue(
        "legal", offer_slug="legal-regulatory-calendar", issue_date=date(2026, 11, 3)
    )
    assert first["status"] == "draft"
    assert first["scope"] == "US"
    assert first["drafted_by"] == "fallback"
    assert len(first["items"]) == 1
    assert first["items"][0]["source_url"] == record().source_url

    channel = await get_channel("legal", enabled_only=False)
    assert channel is not None
    stored = await get_issue(
        industry_id=channel.id,
        offer_slug="legal-regulatory-calendar",
        issue_date=date(2026, 11, 3),
    )
    assert stored is not None
    assert stored["status"] == "draft"

    second = await build_offer_issue(
        "legal", offer_slug="legal-regulatory-calendar", issue_date=date(2026, 11, 3)
    )
    assert second["id"] == first["id"]


@pytest.mark.asyncio
async def test_empty_source_marks_an_empty_issue(clean_db, monkeypatch) -> None:
    async def fake_fetch(*_args, **_kwargs) -> AdapterResult:
        return AdapterResult(records=[], source_version="test-1", source_count=0)

    monkeypatch.setattr(build_module, "fetch_records", fake_fetch)
    result = await build_offer_issue(
        "legal", offer_slug="legal-regulatory-calendar", issue_date=date(2026, 11, 3)
    )
    assert result["status"] == "empty"
    assert result["rows"] == 0


@pytest.mark.asyncio
async def test_unknown_offer_is_not_found(clean_db) -> None:
    from news_api.platform.errors import NotFound

    with pytest.raises(NotFound):
        await build_offer_issue("legal", offer_slug="nope", issue_date=date(2026, 11, 3))
