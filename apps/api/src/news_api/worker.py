"""Redis Streams consumer + scheduler for ingestion."""

from __future__ import annotations

import asyncio
import signal
import time

from news_api.articles.application.queue import (
    consume_once,
    consumer_name,
    ensure_group,
    promote_retries,
    recover_orphans,
    scheduler_tick,
)
from news_api.platform.cache import close_redis, get_redis
from news_api.platform.db import dispose
from news_api.platform.logging import configure_logging, get_logger
from news_api.platform.metrics import QUEUE_DEPTH
from news_api.platform.migrations import run_migrations
from news_api.platform.settings import get_settings

log = get_logger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    log.info(
        "worker.start", env=settings.app_env, refresh_minutes=settings.refresh_interval_minutes
    )
    if settings.run_migrations:
        await run_migrations()
    await ensure_group()
    await recover_orphans()
    stop = asyncio.Event()

    def _stop(signum: int, _frame: object) -> None:
        log.info("worker.stop_signal", signal=signum)
        stop.set()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    consumer = consumer_name()
    last_schedule = 0.0
    try:
        while not stop.is_set():
            now = time.monotonic()
            if now - last_schedule >= 30:
                last_schedule = now
                try:
                    await scheduler_tick()
                    await promote_retries()
                    client = await get_redis()
                    QUEUE_DEPTH.labels(stream="news:jobs").set(await client.xlen("news:jobs"))
                except Exception as exc:
                    log.warning("worker.scheduler_error", error=type(exc).__name__)
            try:
                await consume_once(consumer, block_ms=2000)
            except Exception as exc:
                log.warning("worker.consume_error", error=type(exc).__name__)
                await asyncio.sleep(1.0)
    finally:
        await close_redis()
        await dispose()
        log.info("worker.exit")


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
