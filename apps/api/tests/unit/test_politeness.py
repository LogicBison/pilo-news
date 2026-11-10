"""Fetch-safety SPEC (20261109) §6 matrix: robots, pacing, cooldowns, breaker.

Pure-state tests drive ``pace``/``record`` with a seeded RNG and an explicit
clock; adapter tests use ``FakeRedis`` so nothing here touches the network or
the shared cache.
"""

from __future__ import annotations

import asyncio
import random
import socket

import httpx
import pytest

from news_api.articles.infrastructure.fetcher import _pin_to_address
from news_api.articles.infrastructure.politeness import (
    USER_AGENT,
    HostLedger,
    content_type_allowed,
    empty_state,
    is_challenge,
    pace,
    record,
    robots_allowed,
)

FLOOR = 5.0
CAP = 20
BREAKER_AT = 5
BREAKER_S = 1800.0
NOW = 1_700_000_000.0


def _pace(state, now, *, mode="enforce", floor=FLOOR, cap=CAP, seed=7):
    return pace(
        state,
        now=now,
        floor_s=floor,
        hourly_cap=cap,
        mode=mode,
        breaker_failures=BREAKER_AT,
        breaker_seconds=BREAKER_S,
        rng=random.Random(seed),
    )


# --- pure state machine -----------------------------------------------------


def test_two_attempts_one_host_are_serialised() -> None:
    state = empty_state()
    first = _pace(state, NOW)
    assert first.allowed is True
    second = _pace(state, NOW + 1.0)
    assert second.allowed is False
    assert second.reason == "rate_limited"
    # The floor holds within its jitter band (5 s ±20 %) whatever the seed drew.
    assert 0.0 < second.wait_s <= FLOOR * 1.2


def test_hourly_cap_skips_the_21st_attempt() -> None:
    state = empty_state()
    state["hour_started_at"] = f"{NOW}"
    state["hour_count"] = f"{CAP}"
    decision = _pace(state, NOW + 60.0)
    assert decision.allowed is False
    assert decision.reason == "rate_limited"
    assert decision.note == "hourly_cap"
    # A new hour opens the window again.
    later = _pace(state, NOW + 3601.0)
    assert later.allowed is True


def test_retry_after_is_honoured_as_a_cooldown_floor() -> None:
    state = empty_state()
    record(state, outcome="rate_limited", now=NOW, retry_after=120.0, rng=random.Random(3))
    assert float(state["cooldown_until"]) >= NOW + 120.0
    inside = _pace(state, NOW + 60.0)
    assert inside.allowed is False
    assert inside.reason == "rate_limited"
    outside = _pace(state, NOW + 121.0)
    assert outside.allowed is True


def test_503_escalates_exponentially_without_a_header() -> None:
    state = empty_state()
    record(state, outcome="rate_limited", now=NOW, retry_after=None, rng=random.Random(3))
    first = float(state["cooldown_until"]) - NOW
    record(state, outcome="rate_limited", now=NOW + 10.0, retry_after=None, rng=random.Random(3))
    second = float(state["cooldown_until"]) - (NOW + 10.0)
    # base 60 s, then 120 s, each with ±10 % jitter — strictly longer.
    assert first <= 66.0
    assert second >= 108.0
    assert second > first


def test_breaker_opens_at_five_failures_and_probes_after() -> None:
    state = empty_state()
    for attempt in range(BREAKER_AT):
        record(state, outcome="timeout", now=NOW + attempt, rng=random.Random(1))
    assert float(state["breaker_until"]) == NOW + (BREAKER_AT - 1) + BREAKER_S
    assert state["probe_pending"] == "1"

    open_now = _pace(state, NOW + 60.0)
    assert open_now.allowed is False
    assert open_now.reason == "breaker_open"

    after = _pace(state, NOW + (BREAKER_AT - 1) + BREAKER_S + 1.0)
    assert after.allowed is True
    assert after.note == "probe"
    # The probe spends the reservation and the floor applies to the next one.
    assert state["probe_pending"] == "0"


def test_challenge_body_cools_the_host_for_an_hour() -> None:
    state = empty_state()
    record(state, outcome="challenge", now=NOW, rng=random.Random(1))
    assert state["cooldown_reason"] == "challenge"
    assert float(state["cooldown_until"]) - NOW == 3600.0
    decision = _pace(state, NOW + 600.0)
    assert decision.allowed is False
    assert decision.reason == "challenge"


def test_success_clears_the_streak_and_the_cooldown() -> None:
    state = empty_state()
    record(state, outcome="timeout", now=NOW, rng=random.Random(1))
    record(state, outcome="rate_limited", now=NOW, retry_after=30.0, rng=random.Random(1))
    assert int(state["fail_streak"]) == 2
    record(state, outcome="ok", now=NOW + 5.0, rng=random.Random(1))
    assert state["fail_streak"] == "0"
    assert state["cooldown_until"] == "0"
    assert state["breaker_until"] == "0"


def test_crawl_delay_raises_the_floor_via_the_ledger() -> None:
    async def run() -> None:
        redis = FakeRedis()
        ledger = HostLedger(
            now=lambda: NOW, redis_factory=lambda: _returning(redis), mode="enforce"
        )
        first = await ledger.decide("feeds.example", crawl_delay=7.0)
        assert first.allowed is True
        # The robots delay is persisted as the host's floor and beats the 5 s
        # default: 7 s ±20 % is always strictly longer than a 5 s ±20 % floor.
        stored = await redis.hgetall("fetch:host:feeds.example")
        assert stored["min_floor_s"] == "7.0"
        second = await ledger.decide("feeds.example")
        assert second.allowed is False
        assert second.wait_s >= 7.0 * 0.8

    asyncio.run(run())


# --- adapter: redis down fails open -----------------------------------------


def test_redis_down_still_allows_the_fetch() -> None:
    async def run() -> None:
        def boom():
            raise ConnectionError("redis is down")

        ledger = HostLedger(now=lambda: NOW, redis_factory=boom, mode="enforce")
        decision = await ledger.decide("feeds.example")
        assert decision.allowed is True
        assert decision.note == "pacing_unavailable"
        await ledger.record("feeds.example", "timeout")  # must not raise
        assert await ledger.cooldowns(["feeds.example"]) == {}

    asyncio.run(run())


# --- robots.txt -------------------------------------------------------------


ROBOTS_DISALLOW = b"User-agent: *\nDisallow: /\n"
ROBOTS_DELAY = b"User-agent: *\nCrawl-delay: 7\nAllow: /\n"


def _robots_client(handler) -> tuple[httpx.AsyncClient, list[str]]:
    seen: list[str] = []

    def record_request(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return handler(request)

    return httpx.AsyncClient(transport=httpx.MockTransport(record_request)), seen


@pytest.mark.asyncio
async def test_robots_disallow_blocks_before_any_feed_request() -> None:
    client, seen = _robots_client(lambda _r: httpx.Response(200, content=ROBOTS_DISALLOW))
    async with client:
        allowed, delay = await robots_allowed(
            "https://example.com/feed.xml",
            client=client,
            redis_factory=lambda: _returning(FakeRedis()),
        )
    assert allowed is False
    assert delay == 0.0
    assert seen == ["/robots.txt"]  # the feed itself was never contacted


@pytest.mark.asyncio
async def test_robots_crawl_delay_is_returned() -> None:
    client, _seen = _robots_client(lambda _r: httpx.Response(200, content=ROBOTS_DELAY))
    async with client:
        allowed, delay = await robots_allowed(
            "https://example.com/feed.xml",
            client=client,
            redis_factory=lambda: _returning(FakeRedis()),
        )
    assert allowed is True
    assert delay == 7.0


@pytest.mark.asyncio
async def test_missing_robots_allows_and_is_cached_for_a_day() -> None:
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(404)

    client, _seen = _robots_client(handler)
    redis = FakeRedis()
    async with client:
        for _ in range(2):
            allowed, delay = await robots_allowed(
                "https://example.com/feed.xml",
                client=client,
                redis_factory=lambda: _returning(redis),
            )
            assert (allowed, delay) == (True, 0.0)
    assert calls["n"] == 1  # second lookup came from the cache


@pytest.mark.asyncio
async def test_unreachable_robots_allows() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route")

    client, _seen = _robots_client(handler)
    async with client:
        allowed, delay = await robots_allowed(
            "https://example.com/feed.xml",
            client=client,
            redis_factory=lambda: _returning(FakeRedis()),
        )
    assert (allowed, delay) == (True, 0.0)


# --- DNS pinning (SPEC R8) --------------------------------------------------


@pytest.mark.asyncio
async def test_dns_rebind_pins_the_first_approved_address(monkeypatch) -> None:
    loop = asyncio.get_running_loop()

    async def fake_getaddrinfo(host, port, *, type=0, **_kwargs):  # noqa: A002 - mirrors asyncio
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (
                socket.AF_INET6,
                socket.SOCK_STREAM,
                6,
                "",
                ("2606:2800:220:1:248:1893:25c8:1946", port),
            ),
        ]

    monkeypatch.setattr(loop, "getaddrinfo", fake_getaddrinfo)
    url, headers, extensions = await _pin_to_address(
        "https://example.com/feed.xml", allow_http=False, allow_private=False
    )
    assert url == "https://93.184.216.34/feed.xml"
    assert headers["Host"] == "example.com"
    assert extensions["sni_hostname"] == "example.com"


@pytest.mark.asyncio
async def test_one_private_answer_rejects_the_host(monkeypatch) -> None:
    loop = asyncio.get_running_loop()

    async def fake_getaddrinfo(host, port, *, type=0, **_kwargs):  # noqa: A002 - mirrors asyncio
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", port)),
        ]

    monkeypatch.setattr(loop, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(ValueError, match="not publicly routable"):
        await _pin_to_address("https://example.com/feed.xml", allow_http=False, allow_private=False)


# --- hygiene ----------------------------------------------------------------


def test_challenge_signatures_match_real_pages() -> None:
    assert is_challenge(b"<title>Just a moment...</title>Checking your browser")
    assert is_challenge(b"<div id='cf-chl-test'></div>")
    assert is_challenge(b"Please complete this check: g-recaptcha-response")
    assert not is_challenge(RSS_BODY)
    assert not is_challenge(b"")


def test_content_type_allow_list() -> None:
    assert content_type_allowed("application/rss+xml; charset=utf-8")
    assert content_type_allowed("text/xml")
    assert not content_type_allowed("text/html")
    assert not content_type_allowed(None)


def test_user_agent_carries_the_real_contact_url() -> None:
    assert USER_AGENT.startswith("HeraldFoxBot/")
    assert "https://heraldfox.com/bot" in USER_AGENT
    assert "example" not in USER_AGENT


# --- helpers ----------------------------------------------------------------


RSS_BODY = (
    b"<rss><channel><title>Desk</title>"
    b"<item><title>Rule change</title><link>https://example.com/story</link>"
    b"<description>x</description></item></channel></rss>"
)


class FakeRedis:
    """The subset of redis-py that ``HostLedger`` and the robots cache use."""

    def __init__(self) -> None:
        self.hashes: dict[str, dict[str, str]] = {}
        self.strings: dict[str, str] = {}

    async def set(self, key, value, *, nx=False, px=None, ex=None):  # noqa: ARG002 - parity with redis-py
        if nx and key in self.strings:
            return None
        self.strings[key] = str(value)
        return True

    async def get(self, key):
        return self.strings.get(key)

    async def delete(self, key):
        self.strings.pop(key, None)
        self.hashes.pop(key, None)
        return 1

    async def hgetall(self, key):
        return dict(self.hashes.get(key, {}))

    async def hset(self, key, *, mapping=None):
        self.hashes.setdefault(key, {}).update({str(k): str(v) for k, v in (mapping or {}).items()})
        return 1

    async def expire(self, key, seconds):  # noqa: ARG002 - TTLs are not simulated
        return True


async def _returning(value):
    return value
