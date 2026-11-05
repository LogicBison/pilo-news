from __future__ import annotations

import asyncio
import time
from typing import Any

import structlog

from news_api.articles.domain.dedupe import dedupe_candidates
from news_api.articles.domain.models import Candidate, FeedItem, Topic
from news_api.articles.domain.scoring import score_pool
from news_api.articles.infrastructure.ai_client import AIClient, AIError
from news_api.articles.infrastructure.fetcher import fetch_source
from news_api.articles.infrastructure.normalize import article_uuid, canonicalize_url
from news_api.articles.infrastructure.repo import (
    clear_summaries,
    create_run,
    get_summary_state,
    list_topics,
    mark_run_running,
    purge_old_content,
    set_article_topics,
    set_summary,
    update_run,
    upsert_article,
)
from news_api.channels.infrastructure.repo import get_channel
from news_api.platform.cache import get_json, set_json, single_flight
from news_api.platform.clock import hours_ago, now_iso
from news_api.platform.config import prompt_table, scoring_config, seed_config
from news_api.platform.errors import Conflict, NotFound
from news_api.platform.metrics import (
    ARTICLES_SCORED,
    INGEST_FETCH,
    INGEST_FETCH_DURATION,
    INGEST_ITEMS,
    INGEST_LAG,
    REFRESH_DURATION,
    REFRESH_RUNS,
)
from news_api.platform.settings import get_settings
from news_api.sources.infrastructure.repo import list_fetchable, set_fetch_state

log = structlog.get_logger(__name__)


def _seed_candidates(industry_slug: str, industry_id: str, topics: list[Topic]) -> list[Candidate]:
    config = seed_config()
    by_slug = {topic.slug: topic for topic in topics}
    candidates: list[Candidate] = []
    for item in config.get("items", []):
        if item.get("industry") != industry_slug:
            continue
        canonical = canonicalize_url(str(item["url"]))
        if not canonical:
            continue
        title = str(item["title"])[:300]
        language = str(item["language"])
        seed_topics = tuple(str(topic) for topic in item.get("topics", []))
        candidates.append(
            Candidate(
                industry_id=industry_id,
                source_id=None,
                source_name=str(item.get("publisher") or "Seed"),
                source_trust=1.0,
                title=title,
                url=canonical,
                canonical_url=canonical,
                excerpt=str(item.get("excerpt") or "")[:280],
                publisher=str(item.get("publisher") or ""),
                language=language,
                published_at=hours_ago(float(item.get("published_hours_ago", 12))),
                pinned=True,
                is_seed=True,
                seed_topics=seed_topics,
                article_id=article_uuid(None, canonical, title),
                topics=[by_slug[slug] for slug in seed_topics if slug in by_slug],
            )
        )
    return candidates


def _feed_candidates(
    source: Any, outcome: Any, industry_id: str, topics: list[Topic]
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for item in outcome.items:
        assert isinstance(item, FeedItem)
        canonical = canonicalize_url(item.link)
        if not canonical:
            continue
        candidates.append(
            Candidate(
                industry_id=industry_id,
                source_id=source.id,
                source_name=source.name,
                source_trust=source.trust,
                title=item.title[:300],
                url=canonical,
                canonical_url=canonical,
                excerpt=item.excerpt[:280],
                publisher=item.publisher or source.name,
                language=source.language,
                published_at=item.published_at,
                pinned=False,
                is_seed=False,
                article_id=article_uuid(source.id, canonical, item.title),
                topics=topics,
            )
        )
    return candidates


async def run_ingest(
    industry_slug: str,
    *,
    trigger: str = "manual",
    run_id: str | None = None,
    full_reset: bool = False,
) -> dict[str, Any]:
    settings = get_settings()
    rules = scoring_config()
    channel = await get_channel(industry_slug, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{industry_slug}'.")
    if not channel.enabled:
        raise NotFound(f"No industry with slug '{industry_slug}'.")

    if run_id:
        await mark_run_running(run_id)
    else:
        run_id = await create_run(channel.id, trigger=trigger, status="running")

    started = time.perf_counter()
    stats: dict[str, Any] = {
        "feeds_polled": 0,
        "http_304": 0,
        "items_fetched": 0,
        "new": 0,
        "updated": 0,
        "duplicates": 0,
        "scored_out": 0,
        "summarized": 0,
        "summaries_reused": 0,
        "errors": 0,
        "per_language": {},
    }

    async with single_flight(f"ingest:lock:{industry_slug}", ttl_seconds=1800) as acquired:
        if not acquired:
            await update_run(run_id, status="failed", stats={"error": "lock_held"}, finished=True)
            raise Conflict("A refresh is already running for this channel.")
        try:
            if full_reset:
                cleared = await clear_summaries(channel.id)
                stats["summaries_cleared"] = cleared

            topics = await list_topics(channel.id)
            sources = await list_fetchable(industry_id=channel.id)
            semaphore = asyncio.Semaphore(6)

            async def _one(source: Any) -> Any:
                async with semaphore:
                    fetch_started = time.perf_counter()
                    outcome = await fetch_source(source)
                    INGEST_FETCH.labels(source=source.name, status=outcome.status).inc()
                    INGEST_FETCH_DURATION.labels(source=source.name).observe(
                        time.perf_counter() - fetch_started
                    )
                    await set_fetch_state(
                        source.id,
                        {
                            "success": outcome.status in ("ok", "http_304"),
                            "etag": outcome.etag,
                            "last_modified": outcome.last_modified,
                            "last_error": outcome.error,
                            "blocked": outcome.blocked,
                        },
                    )
                    return outcome

            outcomes = await asyncio.gather(*(_one(source) for source in sources))
            stats["feeds_polled"] = len(outcomes)

            candidates: list[Candidate] = []
            for source, outcome in zip(sources, outcomes, strict=True):
                if outcome.status == "http_304":
                    stats["http_304"] += 1
                    continue
                if outcome.status != "ok":
                    stats["errors"] += 1
                    continue
                stats["items_fetched"] += len(outcome.items)
                candidates.extend(_feed_candidates(source, outcome, channel.id, topics))

            candidates.extend(_seed_candidates(industry_slug, channel.id, topics))

            pools: dict[str, list[Candidate]] = {}
            for candidate in candidates:
                pools.setdefault(candidate.language, []).append(candidate)

            ai = AIClient()
            ai_available = ai.available()
            summary_budget = settings.ai_max_items_per_run if ai_available else 0
            summarized = 0
            language_stats: dict[str, dict[str, int]] = {}

            for language, pool in sorted(pools.items()):
                scored = score_pool(pool, topics)
                stats["scored_out"] += len(pool) - len(scored)
                deduped = dedupe_candidates(scored)
                stats["duplicates"] += len(scored) - len(deduped)
                kept = 0

                for candidate in deduped:
                    ARTICLES_SCORED.labels(industry=industry_slug, result="kept").inc()
                    article_id, inserted = await upsert_article(candidate)
                    candidate.article_id = article_id
                    await set_article_topics(article_id, [topic.id for topic in candidate.topics])
                    if inserted:
                        stats["new"] += 1
                    else:
                        stats["updated"] += 1

                    state = await get_summary_state(article_id)
                    has_summary = bool(
                        state and state.get("summary") and state.get("summary_language") == language
                    )
                    if has_summary and not full_reset:
                        stats["summaries_reused"] += 1
                        kept += 1
                        continue
                    if ai_available and summarized < summary_budget:
                        summary = await ai.summarize(
                            title=candidate.title,
                            excerpt=candidate.excerpt,
                            language=language,
                        )
                        if summary:
                            await set_summary(
                                article_id,
                                summary,
                                source="ai",
                                language=language,
                                version=int(prompt_table(language)["version"]),
                            )
                            stats["summarized"] += 1
                            summarized += 1
                    kept += 1
                    INGEST_ITEMS.labels(industry=industry_slug, result="kept").inc()

                language_stats[language] = {
                    "fetched": len(pool),
                    "kept": kept,
                    "deduped": len(deduped),
                }

                if ai_available:
                    # Generate the desk brief when it is missing, even if this run
                    # added nothing: a failed first attempt would otherwise leave
                    # the channel without a brief until the TTL expires.
                    brief_key = f"bundle:brief:{industry_slug}:{language}"
                    headlines = [candidate.title for candidate in (deduped or pool)[:12]]
                    needs_brief = bool(headlines) and await get_json(brief_key) is None
                    brief = (
                        await ai.desk_brief(headlines=headlines, language=language)
                        if needs_brief
                        else None
                    )
                    if brief:
                        await set_json(
                            f"bundle:brief:{industry_slug}:{language}",
                            {"text": brief, "language": language, "generated_at": now_iso()},
                            ttl_seconds=86400,
                        )
                    picks = await ai.pick_featured(
                        candidates=[
                            {"id": candidate.article_id, "title": candidate.title}
                            for candidate in deduped[:20]
                        ],
                        language=language,
                    )
                    if picks[0]:
                        await set_json(
                            f"bundle:featured:{industry_slug}:{language}",
                            {"lead": picks[0], "favorites": picks[1]},
                            ttl_seconds=86400,
                        )

            stats["per_language"] = language_stats
            purged = await purge_old_content(
                article_days=int(rules.get("purge_after_days", 30)),
                contact_days=int(rules.get("contact_retention_days", 90)),
                lead_months=int(rules.get("lead_retention_months", 24)),
                cta_days=int(rules.get("cta_event_retention_days", 90)),
            )
            stats["purged"] = purged
            duration = time.perf_counter() - started
            stats["duration_ms"] = round(duration * 1000, 2)
            REFRESH_DURATION.labels(industry=industry_slug).observe(duration)
            status = "ok" if stats["errors"] == 0 else "partial"
            await update_run(run_id, status=status, stats=stats, finished=True)
            REFRESH_RUNS.labels(trigger=trigger, status=status).inc()
            INGEST_LAG.labels(industry=industry_slug).observe(duration)
            log.info(
                "ingest.done",
                industry=industry_slug,
                run_id=run_id,
                status=status,
                new=stats["new"],
                errors=stats["errors"],
            )
            return {"run_id": run_id, "status": status, "stats": stats}
        except Exception as exc:
            if isinstance(exc, Conflict | NotFound | AIError):
                raise
            log.error("ingest.failed", industry=industry_slug, error=type(exc).__name__)
            await update_run(
                run_id,
                status="failed",
                stats={**stats, "error": type(exc).__name__},
                finished=True,
            )
            REFRESH_RUNS.labels(trigger=trigger, status="failed").inc()
            raise
