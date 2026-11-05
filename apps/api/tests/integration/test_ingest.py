from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest

from news_api.articles.application import ingest as ingest_module
from news_api.articles.domain.models import FeedItem, FetchOutcome
from news_api.articles.infrastructure.repo import create_run, get_run
from news_api.platform.db import fetch_all, fetch_one
from news_api.platform.errors import Conflict


async def _fake_fetch(source, **_kwargs):
    language = source.language
    return FetchOutcome(
        source.id,
        source.name,
        "ok",
        [
            FeedItem(
                title=(
                    "Regulador publica nuevas reglas de capital"
                    if language == "es"
                    else "Regulator publishes new capital rules"
                ),
                link=f"https://example.com/{source.id}/story",
                published_at=datetime.now(UTC),
                excerpt="A compliance change for professional readers.",
                publisher=source.name,
            )
        ],
    )


@pytest.mark.asyncio
async def test_migrations_are_idempotent() -> None:
    from news_api.platform.migrations import run_migrations

    applied = await run_migrations()
    assert applied == []
    row = await fetch_one("SELECT COUNT(*) AS total FROM schema_migrations")
    assert int(row["total"]) == 3


@pytest.mark.asyncio
async def test_ingest_partitions_languages_and_seeds(monkeypatch) -> None:
    monkeypatch.setattr(ingest_module, "fetch_source", _fake_fetch)
    run_id = await create_run(None, trigger="manual", status="queued")
    result = await ingest_module.run_ingest("legal", trigger="manual", run_id=run_id)
    assert result["status"] == "ok"
    assert result["stats"]["new"] >= 5

    rows = await fetch_all(
        """
        SELECT a.language, COUNT(*) AS total FROM articles a
        JOIN industries i ON i.id = a.industry_id
        WHERE i.slug = 'legal' GROUP BY a.language
        """
    )
    counts = {row["language"]: int(row["total"]) for row in rows}
    assert counts["en"] >= 3
    assert counts["es"] >= 2

    mixed = await fetch_one(
        """
        SELECT COUNT(*) AS total FROM articles a
        JOIN industries i ON i.id = a.industry_id
        WHERE i.slug = 'legal' AND a.language NOT IN ('en', 'es')
        """
    )
    assert int(mixed["total"]) == 0

    run = await get_run(run_id)
    assert run is not None
    assert run["status"] == "ok"
    assert run["stats"]["feeds_polled"] == 2
    assert "per_language" in run["stats"]


@pytest.mark.asyncio
async def test_second_ingest_does_not_duplicate(monkeypatch) -> None:
    monkeypatch.setattr(ingest_module, "fetch_source", _fake_fetch)
    first_run = await create_run(None, trigger="manual", status="queued")
    await ingest_module.run_ingest("legal", trigger="manual", run_id=first_run)
    first_count = await fetch_one("SELECT COUNT(*) AS total FROM articles")
    second_run = await create_run(None, trigger="manual", status="queued")
    second = await ingest_module.run_ingest("legal", trigger="manual", run_id=second_run)
    second_count = await fetch_one("SELECT COUNT(*) AS total FROM articles")
    assert int(first_count["total"]) == int(second_count["total"])
    assert second["stats"]["new"] == 0


@pytest.mark.asyncio
async def test_single_flight_lock_rejects_second_run(monkeypatch) -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def slow_fetch(source, **kwargs):
        started.set()
        await release.wait()
        return await _fake_fetch(source, **kwargs)

    monkeypatch.setattr(ingest_module, "fetch_source", slow_fetch)
    first_run_id = await create_run(None, trigger="manual")
    first = asyncio.create_task(
        ingest_module.run_ingest("legal", trigger="manual", run_id=first_run_id)
    )
    await started.wait()
    run_id = await create_run(None, trigger="manual")
    with pytest.raises(Conflict):
        await ingest_module.run_ingest("legal", trigger="manual", run_id=run_id)
    release.set()
    await first
