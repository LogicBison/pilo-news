"""Worker placeholder. M3 replaces this with the Redis Streams consumer."""

import signal
import time

import structlog

from news_api.platform.settings import get_settings

log = structlog.get_logger()
settings = get_settings()

_running = True


def _stop(signum: int, _frame: object) -> None:
    global _running
    _running = False
    log.info("worker.stop", signal=signum)


def main() -> None:
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    log.info("worker.start", env=settings.app_env)
    while _running:
        time.sleep(30)
    log.info("worker.exit")


if __name__ == "__main__":
    main()
