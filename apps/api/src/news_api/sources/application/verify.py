"""Live verification of every enabled source against the quality policy."""

from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from news_api.articles.domain.models import FetchOutcome
from news_api.articles.infrastructure.fetcher import fetch_source
from news_api.channels.infrastructure import repo as channels_repo
from news_api.sources.application.quality import assess_feed, coverage_warnings
from news_api.sources.domain.models import Source
from news_api.sources.infrastructure import repo as sources_repo

DEFAULT_CONCURRENCY = 6


async def _check(source: Source, semaphore: asyncio.Semaphore) -> dict[str, Any]:
    # Force an unconditional fetch so freshness is measurable.
    probe = replace(
        source,
        etag=None,
        last_modified=None,
        last_fetched_at=None,
        last_success_at=None,
        status="active",
    )
    async with semaphore:
        outcome: FetchOutcome = await fetch_source(probe)
    report = assess_feed(
        source_name=source.name,
        declared_language=source.language,
        trust=source.trust,
        status=outcome.status,
        items=list(outcome.items),
    )
    payload: dict[str, Any] = {
        "name": source.name,
        "feed_url": source.feed_url,
        "language": source.language,
        "trust": source.trust,
        **report.to_dict(),
    }
    if outcome.error:
        payload["error"] = outcome.error
    return payload


async def verify_sources(
    industry: str | None = None, *, concurrency: int = DEFAULT_CONCURRENCY
) -> dict[str, Any]:
    channels = await channels_repo.list_channels(enabled_only=False)
    if industry:
        channels = [channel for channel in channels if channel.slug == industry]
        if not channels:
            raise ValueError(f"unknown industry: {industry}")

    semaphore = asyncio.Semaphore(concurrency)
    now = datetime.now(UTC)
    report: dict[str, Any] = {
        "generated_at": now.isoformat(),
        "industries": [],
        "summary": {"industries": 0, "sources": 0, "passed": 0, "failed": 0},
        "warnings": [],
    }
    for channel in channels:
        sources = await sources_repo.list_sources(channel.id, include_disabled=False)
        results = await asyncio.gather(*(_check(source, semaphore) for source in sources))
        entry = {
            "slug": channel.slug,
            "name": channel.name,
            "sources": results,
            "coverage": [],
        }
        entry["coverage"] = coverage_warnings(
            languages=sorted({source.language for source in sources}),
            enabled_sources=len(sources),
            trust_values=[source.trust for source in sources],
        )
        report["industries"].append(entry)
        report["summary"]["industries"] += 1
        report["summary"]["sources"] += len(results)
        report["summary"]["passed"] += sum(1 for item in results if item["passed"])
        report["summary"]["failed"] += sum(1 for item in results if not item["passed"])
        for warning in entry["coverage"]:
            report["warnings"].append(f"{channel.slug}: {warning}")
    return report
