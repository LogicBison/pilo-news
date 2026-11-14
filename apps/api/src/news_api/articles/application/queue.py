from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import time
from typing import Any

import structlog
from redis.exceptions import ResponseError
from sqlalchemy import text

from news_api.articles.application.ingest import run_ingest
from news_api.articles.infrastructure.repo import (
    active_run,
    create_run,
    get_run,
    last_run,
    update_run,
)
from news_api.channels.infrastructure.repo import list_channels
from news_api.platform import overrides
from news_api.platform.cache import get_redis
from news_api.platform.clock import utcnow
from news_api.platform.db import session_scope
from news_api.platform.settings import get_settings

log = structlog.get_logger(__name__)

STREAM = "news:jobs"
GROUP = "worker"
DEAD = "news:jobs:dead"
RETRY_ZSET = "news:jobs:retry"
RETRY_KEY = "news:job:retry"
# When the last rotation started. Pacing only: the spend ceiling lives in the
# Postgres ledger, so losing this key costs one extra rotation, not money.
ROTATION_KEY = "scheduler:rotation_at"
BACKOFF_SECONDS = (60, 300, 1500)
# Process-local draw for the rotation. Tests pass their own seeded Random.
_rng = random.Random()


def consumer_name() -> str:
    return f"{os.uname().nodename}:{os.getpid()}"


async def recover_orphans() -> int:
    """Single-worker recovery: failed runs and stale locks must not outlive a restart."""
    async with session_scope() as session:
        result = await session.execute(
            text(
                """
                UPDATE refresh_runs SET status = 'failed', finished_at = now(),
                    stats = stats || '{"error": "worker_restart"}'::jsonb
                WHERE status = 'running'
                """
            )
        )
        recovered = int(getattr(result, "rowcount", 0) or 0)
    try:
        client = await get_redis()
        async for key in client.scan_iter("ingest:lock:*"):
            await client.delete(key)
    except Exception:
        pass
    if recovered:
        log.warning("worker.recovered_orphans", runs=recovered)
    return recovered


async def ensure_group() -> None:
    client = await get_redis()
    try:
        await client.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
    except Exception as exc:
        if "BUSYGROUP" not in str(exc):
            raise


async def enqueue(*, run_id: str, industry: str, trigger: str, full_reset: bool = False) -> str:
    client = await get_redis()
    return str(
        await client.xadd(
            STREAM,
            {
                "run_id": run_id,
                "industry": industry,
                "trigger": trigger,
                "full_reset": "1" if full_reset else "0",
                "attempts": "0",
            },
        )
    )


async def enqueue_offer(*, issue_id: str, industry: str, offer: str, issue_date: str) -> str:
    client = await get_redis()
    return str(
        await client.xadd(
            STREAM,
            {
                "kind": "offer",
                "issue_id": issue_id,
                "industry": industry,
                "offer": offer,
                "issue_date": issue_date,
                "attempts": "0",
            },
        )
    )


async def promote_retries() -> int:
    client = await get_redis()
    now = time.time()
    due = await client.zrangebyscore(RETRY_ZSET, 0, now, start=0, num=20)
    promoted = 0
    for run_id in due:
        raw = await client.get(f"{RETRY_KEY}:{run_id}")
        if raw:
            payload = json.loads(raw)
            await client.xadd(STREAM, payload)
        await client.zrem(RETRY_ZSET, run_id)
        await client.delete(f"{RETRY_KEY}:{run_id}")
        promoted += 1
    return promoted


async def schedule_retry(fields: dict[str, str]) -> bool:
    attempts = int(fields.get("attempts", "0")) + 1
    if attempts >= 3:
        return False
    delay = BACKOFF_SECONDS[min(attempts - 1, len(BACKOFF_SECONDS) - 1)]
    client = await get_redis()
    payload = {**fields, "attempts": str(attempts)}
    await client.set(f"{RETRY_KEY}:{fields['run_id']}", json.dumps(payload), ex=86400)
    await client.zadd(RETRY_ZSET, {fields["run_id"]: time.time() + delay})
    return True


async def dead_letter(fields: dict[str, str], error: str) -> None:
    client = await get_redis()
    payload: dict[str, Any] = dict(fields)
    payload["error"] = error[:300]
    await client.xadd(DEAD, payload)
    await update_run(fields["run_id"], status="failed", stats={"error": error[:300]}, finished=True)
    log.error("worker.dead_letter", industry=fields.get("industry"), error=error[:120])


def _stagger(industry: str) -> int:
    digest = hashlib.sha256(industry.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 600


async def scheduler_tick(*, rng: random.Random | None = None) -> int:
    """Start the due desks - a weighted-random subset of them, not all at once.

    Two gates stack. The per-channel interval decides whether a desk is *due*;
    the rotation window decides how many due desks may *start* now. With twelve
    channels and a tight budget, running every due desk on the same tick gives
    each of them one summary; rotating gives a few of them a full run and comes
    back for the others later, which is more useful per dollar. The draw is
    weighted by staleness, so a desk that keeps losing gets heavier until it
    wins - no channel is starved, and the order is not guessable.

    The rotation window lives in Redis. Losing it costs one extra rotation, not
    a cent: the spend ceiling is enforced by the Postgres ledger, not here.
    """
    settings = get_settings()
    default_interval = settings.refresh_interval_minutes
    per_tick = max(
        0, await overrides.effective_int("ai_desks_per_tick", int(settings.ai_desks_per_tick))
    )
    window_minutes = max(
        0, await overrides.effective_int("ai_rotation_minutes", int(settings.ai_rotation_minutes))
    )
    now = utcnow()
    due: list[tuple[Any, float]] = []
    for channel in await list_channels(enabled_only=True):
        if not channel.auto_fetch_enabled:
            continue
        interval_minutes = channel.effective_fetch_interval(default_interval)
        interval_seconds = interval_minutes * 60
        previous = await last_run(channel.id, trigger="schedule")
        if previous:
            started = previous["started_at"]
            if hasattr(started, "timestamp"):
                elapsed = now.timestamp() - started.timestamp()
            else:
                elapsed = interval_seconds
            if elapsed < interval_seconds + _stagger(channel.slug):
                continue
            weight = elapsed / max(1, interval_seconds)
        else:
            # Never run: the keenest candidate, but still one draw among many.
            weight = 2.0
        if await active_run(channel.id):
            continue
        due.append((channel, weight))
    if not due:
        return 0
    if len(due) > per_tick and not await _rotation_open(window_minutes):
        return 0
    picked = select_desks(due, per_tick=per_tick, rng=rng)
    enqueued = 0
    for channel in picked:
        run_id = await create_run(channel.id, trigger="schedule", requested_by="scheduler")
        await enqueue(run_id=run_id, industry=channel.slug, trigger="schedule")
        enqueued += 1
        log.info(
            "scheduler.enqueued",
            industry=channel.slug,
            run_id=run_id,
            interval_minutes=channel.effective_fetch_interval(default_interval),
            schedule_source="channel" if channel.fetch_interval_minutes else "default",
        )
    if enqueued:
        await _mark_rotation()
    if len(due) > enqueued:
        log.info(
            "scheduler.rotated",
            due=len(due),
            started=enqueued,
            deferred=[channel.slug for channel, _ in due if channel not in picked],
        )
    return enqueued


def select_desks(
    due: list[tuple[Any, float]], *, per_tick: int, rng: random.Random | None = None
) -> list[Any]:
    """Weighted sampling without replacement over the due desks."""
    if per_tick <= 0 or not due:
        return []
    if len(due) <= per_tick:
        return [channel for channel, _ in due]
    draw = _rng if rng is None else rng
    pool = list(due)
    picked: list[Any] = []
    for _ in range(per_tick):
        # A floor on the weight: a desk that just missed the draw stays in it.
        weights = [max(0.05, weight) for _, weight in pool]
        choice = draw.choices(pool, weights=weights, k=1)[0]
        picked.append(choice[0])
        pool.remove(choice)
    return picked


async def _rotation_open(window_minutes: int) -> bool:
    """Whether a rotation may start now. An unreadable marker means yes."""
    if window_minutes <= 0:
        return True
    try:
        client = await get_redis()
        raw = await client.get(ROTATION_KEY)
    except Exception as exc:  # pacing is not a safety control
        log.warning("scheduler.rotation_marker_unreadable", error=type(exc).__name__)
        return True
    if not raw:
        return True
    try:
        return time.time() - float(raw) >= window_minutes * 60
    except (TypeError, ValueError):
        return True


async def _mark_rotation() -> None:
    try:
        client = await get_redis()
        await client.set(ROTATION_KEY, str(time.time()), ex=86400)
    except Exception as exc:  # pragma: no cover - pacing only
        log.warning("scheduler.rotation_marker_unwritable", error=type(exc).__name__)


async def _process_offer_job(fields: dict[str, str]) -> None:
    from datetime import date

    from news_api.offers.application.build import build_offer_issue

    try:
        await build_offer_issue(
            fields["industry"],
            offer_slug=fields["offer"],
            issue_date=date.fromisoformat(fields["issue_date"]),
        )
    except Exception as exc:
        # build_offer_issue already marks the issue failed; retry happens on a
        # later scheduler tick after the retry window.
        log.warning(
            "worker.offer_failed",
            industry=fields.get("industry"),
            offer=fields.get("offer"),
            issue_date=fields.get("issue_date"),
            error=type(exc).__name__,
        )


async def process_job(job_id: str, fields: dict[str, str]) -> None:
    if fields.get("kind") == "offer":
        await _process_offer_job(fields)
        return
    try:
        await run_ingest(
            fields["industry"],
            trigger=fields.get("trigger", "manual"),
            run_id=fields["run_id"],
            full_reset=fields.get("full_reset") == "1",
        )
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        if await schedule_retry(fields):
            log.warning(
                "worker.retry_scheduled",
                industry=fields.get("industry"),
                attempt=fields.get("attempts"),
                error=type(exc).__name__,
            )
        else:
            await dead_letter(fields, error)
        raise
    else:
        log.info("worker.job_done", industry=fields.get("industry"), run_id=fields.get("run_id"))


async def _reclaim_pending(client: Any, consumer: str) -> int:
    try:
        response = await client.xautoclaim(
            STREAM, GROUP, consumer, min_idle_time=60_000, start_id="0-0", count=5
        )
    except Exception:
        return 0
    entries = response[1] if isinstance(response, tuple | list) and len(response) > 1 else []
    processed = 0
    for job_id, raw_fields in entries:
        fields = {str(key): str(value) for key, value in raw_fields.items()}
        try:
            await process_job(str(job_id), fields)
        except Exception:
            pass
        finally:
            try:
                await client.xack(STREAM, GROUP, job_id)
            except Exception:
                pass
        processed += 1
    return processed


async def consume_once(consumer: str, *, block_ms: int = 3000, count: int = 5) -> int:
    client = await get_redis()
    reclaimed = await _reclaim_pending(client, consumer)
    try:
        response = await client.xreadgroup(
            GROUP, consumer, {STREAM: ">"}, count=count, block=block_ms
        )
    except ResponseError as exc:
        if "NOGROUP" in str(exc):
            await ensure_group()
            return reclaimed
        raise
    if not response:
        return reclaimed
    processed = 0
    for _stream, entries in response:
        for job_id, raw_fields in entries:
            fields = {str(key): str(value) for key, value in raw_fields.items()}
            try:
                await process_job(str(job_id), fields)
            except Exception:
                pass
            finally:
                try:
                    await client.xack(STREAM, GROUP, job_id)
                except Exception:
                    log.warning("worker.ack_failed", job_id=str(job_id))
            processed += 1
    return processed + reclaimed


async def wait_for_run(run_id: str, timeout_seconds: float = 90.0) -> dict[str, Any] | None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        run = await get_run(run_id)
        if run and run["status"] in ("ok", "partial", "failed"):
            return run
        await asyncio.sleep(1.0)
    return await get_run(run_id)
