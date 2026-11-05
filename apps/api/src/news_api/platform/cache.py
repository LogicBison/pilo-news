from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as aioredis
import structlog

from news_api.platform.settings import get_settings

log = structlog.get_logger(__name__)
_settings = get_settings()

_client: aioredis.Redis | None = None
_client_loop: int | None = None


async def get_redis() -> aioredis.Redis:
    global _client, _client_loop
    loop_id = id(asyncio.get_running_loop())
    if _client is not None and _client_loop != loop_id:
        try:
            await _client.aclose()  # type: ignore[attr-defined]
        except Exception:
            pass
        _client = None
    if _client is None:
        _client = aioredis.from_url(
            _settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=3,
        )
        _client_loop = loop_id
    return _client


async def close_redis() -> None:
    global _client, _client_loop
    if _client is not None:
        try:
            await _client.aclose()  # type: ignore[attr-defined]
        except Exception:
            pass
        _client = None
        _client_loop = None


async def ping() -> bool:
    try:
        client = await get_redis()
        return bool(await client.ping())
    except Exception as exc:  # pragma: no cover - dependency failure path
        log.warning("redis.unavailable", error=type(exc).__name__)
        return False


async def rate_limit(key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
    """Fixed-window counter. Returns (allowed, remaining, reset_epoch_seconds).

    Redis loss fails open: availability beats a perfect limiter for public reads.
    """
    now = int(time.time())
    window = now // window_seconds
    reset = (window + 1) * window_seconds
    redis_key = f"rl:{key}:{window}"
    try:
        client = await get_redis()
        pipe = client.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, window_seconds + 5)
        count, _ = await pipe.execute()
        used = int(count)
        return used <= limit, max(0, limit - used), reset
    except Exception as exc:  # pragma: no cover - dependency failure path
        log.warning("redis.rate_limit_unavailable", error=type(exc).__name__)
        return True, limit, reset


async def increment(key: str, amount: float = 1.0) -> float:
    try:
        client = await get_redis()
        return float(await client.incrbyfloat(key, amount))
    except Exception:
        return 0.0


async def get_float(key: str) -> float:
    try:
        client = await get_redis()
        value = await client.get(key)
        return float(value) if value is not None else 0.0
    except Exception:
        return 0.0


async def set_json(key: str, value: Any, ttl_seconds: int | None = None) -> None:
    try:
        client = await get_redis()
        await client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except Exception as exc:  # pragma: no cover - cache is disposable
        log.warning("redis.set_failed", key=key, error=type(exc).__name__)


async def get_json(key: str) -> Any | None:
    try:
        client = await get_redis()
        raw = await client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


@asynccontextmanager
async def single_flight(key: str, ttl_seconds: int = 1800) -> AsyncIterator[bool]:
    """Yield True when the lock is acquired; always release only our own token."""
    token = f"{time.time_ns()}"
    acquired = False
    try:
        client = await get_redis()
        acquired = bool(await client.set(key, token, nx=True, ex=ttl_seconds))
    except Exception as exc:  # pragma: no cover - dependency failure path
        log.warning("redis.lock_unavailable", key=key, error=type(exc).__name__)
    try:
        yield acquired
    finally:
        if acquired:
            try:
                client = await get_redis()
                current = await client.get(key)
                if current == token:
                    await client.delete(key)
            except Exception:  # pragma: no cover
                log.warning("redis.unlock_failed", key=key)


async def lock_holder(key: str) -> bool:
    try:
        client = await get_redis()
        return bool(await client.exists(key))
    except Exception:
        return False
