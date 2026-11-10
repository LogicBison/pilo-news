"""Polite fetching: identity, robots.txt, per-host pacing, cooldowns, breaker.

Every piece of state lives in Redis (fetch-safety SPEC 20261109 §4), so nothing
here is a schema change and losing it costs one unpaced cycle, never a wrong
fetch. Everything fails open: if Redis cannot be reached the fetch runs
unpaced and logs ``fetch.pacing_unavailable`` — an outage of the cache must
never become an outage of ingestion.

The three decisions kept deliberately separate:

- ``pace`` / ``record`` are pure functions over a state dict. Tests drive them
  with a fake clock and no Redis.
- ``HostLedger`` is the Redis adapter around them (lock, TTL, fail-open).
- ``robots_allowed`` is the one network call this module makes on its own, and
  it validates the URL exactly like the feed fetch does.
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx
import structlog

from news_api.platform.settings import get_settings

log = structlog.get_logger(__name__)

_settings = get_settings()

# Shared jitter source; tests pass a seeded Random instead.
_RNG = random.Random()

#: The one identity both fetchers present (SPEC R1). Built once from settings
#: so a deployment that overrides BOT_NAME changes it everywhere at once.
USER_AGENT = f"{_settings.bot_name}/{_settings.bot_version} (+{_settings.bot_url})"

#: Content types accepted for a feed without falling back to "does it parse".
FEED_CONTENT_TYPES = frozenset(
    {
        "application/rss+xml",
        "application/atom+xml",
        "application/xml",
        "text/xml",
        "application/rdf+xml",
    }
)

#: Anti-bot challenge bodies, grouped: a group matches when *all* its needles
#: are present in the first 2 KiB (SPEC R6).
CHALLENGE_SIGNATURES: tuple[tuple[bytes, ...], ...] = (
    (b"just a moment", b"cloudflare"),
    (b"checking your browser",),
    (b"cf-chl-",),
    (b"incapsula incident id",),
    (b"request blocked", b"aws"),
    (b"g-recaptcha-response",),
    (b"are you a robot",),
)

#: Outcome -> metric reason for ``ingest_fetch_blocked_total{reason}``.
BLOCK_REASONS: dict[str, str] = {
    "robots_disallowed": "robots",
    "rate_limited": "rate_limited",
    "challenge": "challenge",
    "blocked": "ssrf",
    "too_large": "size",
    "denied": "denied",
}

STATE_FIELDS = (
    "next_allowed_at",
    "hour_count",
    "hour_started_at",
    "fail_streak",
    "cooldown_until",
    "cooldown_reason",
    "breaker_until",
    "probe_pending",
    "min_floor_s",
)


def empty_state() -> dict[str, str]:
    """A blank per-host ledger row."""
    return {field: "0" for field in STATE_FIELDS} | {"cooldown_reason": ""}


def is_challenge(body: bytes) -> bool:
    """True when the body looks like an anti-bot challenge rather than a feed."""
    head = body[:2048].lower()
    return any(all(needle in head for needle in group) for group in CHALLENGE_SIGNATURES)


def content_type_allowed(value: str | None) -> bool:
    """``True`` for the feed types we accept outright (parameters ignored)."""
    if not value:
        return False
    return value.split(";", 1)[0].strip().lower() in FEED_CONTENT_TYPES


def _f(state: dict[str, str], key: str) -> float:
    try:
        return float(state.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


@dataclass(frozen=True)
class Decision:
    """What the ledger says about one attempted request to one host."""

    allowed: bool
    reason: str = ""
    wait_s: float = 0.0
    note: str = ""


def pace(
    state: dict[str, str],
    *,
    now: float,
    floor_s: float,
    hourly_cap: int,
    mode: str,
    breaker_failures: int,
    breaker_seconds: float,
    rng: random.Random | None = None,
) -> Decision:
    """Decide whether a request to this host may go out now.

    In ``shadow``/``off`` the floor, cap and breaker are computed but do not
    block; the decision still reports what *would* have happened so the log can
    show it. A cooldown that came from an explicit ``Retry-After`` is honoured
    in every mode — that one the server asked for by name.
    """
    rng = rng if rng is not None else _RNG
    cooldown_until = _f(state, "cooldown_until")
    if cooldown_until > now:
        return Decision(
            False,
            state.get("cooldown_reason") or "rate_limited",
            wait_s=cooldown_until - now,
            note="cooldown",
        )

    enforcing = mode == "enforce"
    floor = max(floor_s, _f(state, "min_floor_s"))
    # ±20 % jitter so two workers with the same clock do not align.
    floor *= 1 + rng.uniform(-0.2, 0.2)

    if _f(state, "breaker_until") > now:
        if enforcing:
            return Decision(False, "breaker_open", _f(state, "breaker_until") - now, "breaker")
        return Decision(True, note="shadow:breaker_open")

    hour_started = _f(state, "hour_started_at")
    hour_count = int(_f(state, "hour_count"))
    if now - hour_started >= 3600:
        hour_started, hour_count = now, 0
    if hourly_cap > 0 and hour_count >= hourly_cap:
        wait = max(0.0, hour_started + 3600 - now)
        if enforcing:
            return Decision(False, "rate_limited", wait, "hourly_cap")
        return Decision(True, note="shadow:hourly_cap")

    next_allowed = _f(state, "next_allowed_at")
    probe = state.get("probe_pending") == "1"
    if not probe and next_allowed > now:
        if enforcing:
            return Decision(False, "rate_limited", next_allowed - now, "floor")
        return Decision(True, note="shadow:floor")

    # Reserve the slot before the request goes out: the floor has to hold even
    # when two fetches race, which read-after-write alone would not guarantee.
    state["hour_started_at"] = f"{hour_started}"
    state["hour_count"] = f"{hour_count + 1}"
    state["next_allowed_at"] = f"{now + floor}"
    if probe:
        state["probe_pending"] = "0"
    return Decision(True, note="probe" if probe else "")


def record(
    state: dict[str, str],
    *,
    outcome: str,
    now: float,
    retry_after: float | None = None,
    rng: random.Random | None = None,
) -> None:
    """Fold one fetch outcome back into the host's ledger."""
    settings = get_settings()
    rng = rng if rng is not None else _RNG
    streak = int(_f(state, "fail_streak"))

    if outcome in ("ok", "http_304"):
        state.update(
            {
                "fail_streak": "0",
                "cooldown_until": "0",
                "cooldown_reason": "",
                "breaker_until": "0",
                "probe_pending": "0",
            }
        )
        return

    if outcome in ("http_4xx",):
        # Not the host's fault and not ours to escalate: a permanent 404 is a
        # feed problem, so it resets the streak instead of tripping anything.
        state.update({"fail_streak": "0", "cooldown_until": "0", "cooldown_reason": ""})
        return

    if outcome == "denied":
        # A publisher said no (401/403, robots, licence). Retrying every cycle
        # is how a polite crawler becomes a pest, so park the host for a week.
        state.update(
            {
                "cooldown_until": f"{now + settings.fetch_denied_cooldown_s}",
                "cooldown_reason": "denied",
            }
        )
        return

    streak += 1
    state["fail_streak"] = f"{streak}"

    if outcome == "rate_limited":
        # 429/503: never retry immediately. Retry-After wins when it is longer
        # than our own escalation (SPEC R4) — and jitter only ever applies to
        # our own estimate, so a server-given floor is never undercut.
        escalate = settings.fetch_retry_base_s * (2 ** max(streak - 1, 0))
        escalate *= 1 + rng.uniform(-0.1, 0.1)
        cooldown = max(retry_after or 0.0, escalate)
        cooldown = min(cooldown, float(settings.fetch_cooldown_cap_s))
        state["cooldown_until"] = f"{now + cooldown}"
        state["cooldown_reason"] = "rate_limited"
        _open_breaker_if_tripped(state, now, streak)
        return

    if outcome == "challenge":
        state["cooldown_until"] = f"{now + settings.fetch_challenge_cooldown_s}"
        state["cooldown_reason"] = "challenge"
        return

    # timeout / connection error / 5xx feed the breaker.
    _open_breaker_if_tripped(state, now, streak)


def _open_breaker_if_tripped(state: dict[str, str], now: float, streak: int) -> None:
    settings = get_settings()
    if streak >= settings.fetch_breaker_failures:
        state["breaker_until"] = f"{now + settings.fetch_breaker_seconds}"
        state["probe_pending"] = "1"


class HostLedger:
    """Redis adapter for :func:`pace` / :func:`record`.

    The clock is injectable so tests can advance it instead of sleeping, and
    every Redis failure degrades to "allowed, unpaced, logged".
    """

    def __init__(
        self,
        *,
        now: Callable[[], float] | None = None,
        redis_factory: Callable[[], Awaitable[Any]] | None = None,
        mode: str | None = None,
    ) -> None:
        self._now = now or time.time
        self._redis_factory = redis_factory
        # ``mode`` overrides FETCH_PACING for one instance; tests use it to
        # drive the state machine directly instead of monkeypatching globals.
        self._mode = mode
        self._unavailable_logged = False

    def now(self) -> float:
        """The ledger clock (injectable so tests never sleep)."""
        return self._now()

    def _pacing_mode(self) -> str:
        return self._mode or get_settings().fetch_pacing

    async def _redis(self) -> Any | None:
        if self._redis_factory is not None:
            try:
                return await self._redis_factory()
            except Exception:  # pragma: no cover - injected failure path
                return None
        try:
            from news_api.platform.cache import get_redis

            return await get_redis()
        except Exception:  # pragma: no cover - dependency failure path
            return None

    def _warn_unavailable(self, error: Exception) -> None:
        if not self._unavailable_logged:
            log.warning("fetch.pacing_unavailable", error=type(error).__name__)
            self._unavailable_logged = True

    async def decide(self, host: str, *, crawl_delay: float = 0.0) -> Decision:
        """Reserve a slot for ``host``, or explain why we may not go yet."""
        settings = get_settings()
        if self._pacing_mode() == "off":
            return Decision(True, note="pacing_off")

        key = f"fetch:host:{host}"
        redis = await self._redis()
        if redis is None:
            return Decision(True, note="pacing_unavailable")

        lock_key = f"{key}:lock"
        try:
            locked = await redis.set(lock_key, "1", nx=True, px=10_000)
            if not locked:
                # Another fetch is reserving this host right now; refusing is
                # correct, because the floor is exactly what it is writing.
                return Decision(False, "rate_limited", 1.0, "lock_held")
            state = {str(k): str(v) for k, v in (await redis.hgetall(key)).items()} or empty_state()
            if crawl_delay > max(float(state.get("min_floor_s") or 0), 0):
                state["min_floor_s"] = f"{crawl_delay}"
                await redis.hset(key, mapping={"min_floor_s": state["min_floor_s"]})
            decision = pace(
                state,
                now=self._now(),
                floor_s=settings.fetch_host_floor_s,
                hourly_cap=settings.fetch_host_hourly_cap,
                mode=self._pacing_mode(),
                breaker_failures=settings.fetch_breaker_failures,
                breaker_seconds=settings.fetch_breaker_seconds,
            )
            if decision.allowed and state.get("hour_count"):
                await redis.hset(key, mapping=state)
                await redis.expire(key, 26 * 3600)
            if not decision.allowed:
                log.info(
                    "fetch.paced_out",
                    host=host,
                    reason=decision.reason,
                    wait_s=round(decision.wait_s, 2),
                    note=decision.note,
                )
            return decision
        except Exception as exc:  # pragma: no cover - dependency failure path
            self._warn_unavailable(exc)
            return Decision(True, note="pacing_unavailable")
        finally:
            try:
                await redis.delete(lock_key)
            except Exception:  # pragma: no cover - best effort
                pass

    async def record(self, host: str, outcome: str, *, retry_after: float | None = None) -> None:
        """Fold an outcome back into the host row. Never raises."""
        if self._pacing_mode() == "off":
            return
        redis = await self._redis()
        if redis is None:
            return
        key = f"fetch:host:{host}"
        try:
            state = {str(k): str(v) for k, v in (await redis.hgetall(key)).items()} or empty_state()
            record(state, outcome=outcome, now=self._now(), retry_after=retry_after)
            await redis.hset(key, mapping=state)
            await redis.expire(key, 26 * 3600)
            # R9 asks for 0 on success: a gauge left at the last cooldown
            # value would keep reporting a pause that has ended.
            cooldown = max(0.0, float(state.get("cooldown_until") or 0) - self._now())
            from news_api.platform.metrics import INGEST_HOST_COOLDOWN

            INGEST_HOST_COOLDOWN.labels(host=host).set(cooldown)
        except Exception as exc:  # pragma: no cover - dependency failure path
            self._warn_unavailable(exc)

    async def cooldowns(self, hosts: Iterable[str]) -> dict[str, dict[str, Any]]:
        """``{host: {cooldown_until, cooldown_reason, fail_streak}}`` for R10."""
        redis = await self._redis()
        if redis is None:
            return {}
        out: dict[str, dict[str, Any]] = {}
        try:
            for host in dict.fromkeys(hosts):
                raw = await redis.hgetall(f"fetch:host:{host}")
                state = {str(k): str(v) for k, v in raw.items()}
                until = float(state.get("cooldown_until") or 0)
                if until > self._now() or int(state.get("fail_streak") or 0):
                    out[host] = {
                        "cooldown_until": until if until > self._now() else 0.0,
                        "cooldown_reason": state.get("cooldown_reason") or "",
                        "fail_streak": int(state.get("fail_streak") or 0),
                    }
        except Exception as exc:  # pragma: no cover - dependency failure path
            self._warn_unavailable(exc)
            return {}
        return out


async def _load_robots(
    url: str,
    *,
    user_agent: str,
    client: httpx.AsyncClient | None,
    validator: Callable[[str], Awaitable[str]] | None,
    now: float,
    ttl_s: int,
    redis_factory: Callable[[], Awaitable[Any]] | None,
) -> str:
    """The robots body for ``url``'s host, from Redis or the network.

    Redirects are followed by hand (max 3) so every hop is validated: the
    earlier version reused a non-following client, read a ``301`` as "no
    rules", and quietly fetched hosts whose canonical robots.txt says no.
    """
    parts = urlsplit(url)
    host = parts.hostname or ""
    if not host:
        return ""
    key = f"fetch:robots:{host}"
    redis: Any | None = None
    try:
        if redis_factory is not None:
            redis = await redis_factory()
        else:
            from news_api.platform.cache import get_redis

            redis = await get_redis()
    except Exception:  # pragma: no cover - dependency failure path
        redis = None

    if redis is not None:
        try:
            cached = await redis.get(key)
            if cached is not None:
                payload = json.loads(cached)
                return str(payload.get("body") or "")
        except Exception:  # pragma: no cover - cache read failure
            pass

    robots_url = urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=httpx.Timeout(6.0, connect=4.0))
    body = ""
    try:
        for _ in range(4):
            async with http.stream(
                "GET", robots_url, headers={"User-Agent": user_agent, "Accept": "text/plain,*/*"}
            ) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        return ""
                    robots_url = urljoin(robots_url, location)
                    if validator is not None:
                        robots_url = await validator(robots_url)
                    continue
                if response.status_code == 200:
                    chunks: list[bytes] = []
                    total = 0
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if total > 64 * 1024:
                            break
                        chunks.append(chunk)
                    body = b"".join(chunks).decode("utf-8", "replace")
                break
    except (httpx.HTTPError, TimeoutError):
        # Unreadable robots.txt means allow; failures are not cached.
        return ""
    finally:
        if owns_client:
            await http.aclose()

    if redis is not None:
        try:
            await redis.set(key, json.dumps({"at": now, "body": body}), ex=ttl_s)
        except Exception:  # pragma: no cover - cache write failure
            pass
    return body


def _verdict(body: str, url: str, user_agent: str) -> tuple[bool, float]:
    parser = RobotFileParser()
    parser.parse((body or "").splitlines())
    if not parser.can_fetch(user_agent, url):
        return False, 0.0
    crawl_delay = parser.crawl_delay(user_agent)
    return True, float(crawl_delay or 0.0)


async def robots_allowed(
    url: str,
    *,
    user_agent: str = USER_AGENT,
    client: httpx.AsyncClient | None = None,
    validator: Callable[[str], Awaitable[str]] | None = None,
    now: float | None = None,
    ttl_s: int | None = None,
    redis_factory: Callable[[], Awaitable[Any]] | None = None,
) -> tuple[bool, float]:
    """``(allowed, crawl_delay)`` for one feed URL, per SPEC R2.

    Missing or unreadable robots.txt means allow — the standard reading, and
    the right one for feeds. The raw body is cached for a day so a restart does
    not re-fetch it, and a disallowing document is never followed by a request
    to the feed itself.
    """
    settings = get_settings()
    stamp = now if now is not None else time.time()
    ttl = ttl_s if ttl_s is not None else settings.fetch_robots_ttl_s
    try:
        body = await _load_robots(
            url,
            user_agent=user_agent,
            client=client,
            validator=validator,
            now=stamp,
            ttl_s=ttl,
            redis_factory=redis_factory,
        )
    except ValueError:
        # The robots host is not publishable: neither is the feed.
        return False, 0.0
    return _verdict(body, url, user_agent)


async def robots_snapshot(
    url: str,
    *,
    user_agent: str = USER_AGENT,
    client: httpx.AsyncClient | None = None,
    validator: Callable[[str], Awaitable[str]] | None = None,
    now: float | None = None,
    ttl_s: int | None = None,
    redis_factory: Callable[[], Awaitable[Any]] | None = None,
) -> tuple[bool, float, str]:
    """``(allowed, crawl_delay, sha256)`` — the permission record for verify.

    The hash is what makes the ledger auditable: it names the exact robots text
    the verdict came from, so a later change is visible without storing the
    document itself.
    """
    settings = get_settings()
    stamp = now if now is not None else time.time()
    ttl = ttl_s if ttl_s is not None else settings.fetch_robots_ttl_s
    try:
        body = await _load_robots(
            url,
            user_agent=user_agent,
            client=client,
            validator=validator,
            now=stamp,
            ttl_s=ttl,
            redis_factory=redis_factory,
        )
    except ValueError:
        return False, 0.0, ""
    allowed, delay = _verdict(body, url, user_agent)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest() if body else ""
    return allowed, delay, digest


__all__ = [
    "BLOCK_REASONS",
    "CHALLENGE_SIGNATURES",
    "Decision",
    "FEED_CONTENT_TYPES",
    "HostLedger",
    "STATE_FIELDS",
    "USER_AGENT",
    "content_type_allowed",
    "empty_state",
    "is_challenge",
    "pace",
    "record",
    "robots_allowed",
    "robots_snapshot",
]
