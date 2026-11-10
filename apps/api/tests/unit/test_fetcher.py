import httpx
import pytest

from news_api.articles.infrastructure.fetcher import fetch_source
from news_api.articles.infrastructure.politeness import HostLedger
from news_api.sources.domain.models import Source
from news_api.sources.domain.validation import validate_feed_url
from tests.unit.test_politeness import FakeRedis


def make_source(**overrides) -> Source:
    values = {
        "id": "00000000-0000-0000-0000-000000000001",
        "industry_id": "00000000-0000-0000-0000-000000000002",
        "name": "Example Feed",
        "feed_url": "https://example.com/feed.xml",
        "language": "en",
        "trust": 0.8,
        "enabled": True,
        "allow_http": False,
        "poll_interval_min": 720,
        "terms_checked_at": None,
        "terms_url": None,
        "etag": None,
        "last_modified": None,
        "last_fetched_at": None,
        "last_success_at": None,
        "status": "active",
        "consecutive_failures": 0,
        "last_error": None,
    }
    values.update(overrides)
    return Source(**values)


# Hermetic fetches: no robots.txt request, no Redis host pacing.
HERMETIC = {"check_robots": False, "ledger": HostLedger(mode="off")}


async def _as_redis(value):
    return value


RSS = b"""<rss><channel><title>Desk</title>
<item><title>Regulator updates compliance rules</title>
<link>https://example.com/story</link><description>Rule change.</description>
<pubDate>Wed, 05 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>"""


@pytest.mark.asyncio
async def test_fetch_parses_feed_and_sends_conditional_headers() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["if_none_match"] = request.headers.get("if-none-match")
        return httpx.Response(
            200,
            content=RSS,
            headers={"etag": '"v1"', "content-type": "application/rss+xml"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(
            make_source(etag='"old"'), client=client, allow_private=True, **HERMETIC
        )
    assert outcome.status == "ok"
    assert outcome.items[0].title == "Regulator updates compliance rules"
    assert seen["if_none_match"] == '"old"'


@pytest.mark.asyncio
async def test_fetch_304_is_success_without_parsing() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(304, headers={"etag": '"same"'})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(make_source(), client=client, allow_private=True, **HERMETIC)
    assert outcome.status == "http_304"
    assert outcome.items == []


@pytest.mark.asyncio
async def test_fetch_blocks_redirect_to_metadata() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://169.254.169.254/latest/meta-data"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(make_source(), client=client, allow_private=True, **HERMETIC)
    assert outcome.status == "blocked"
    assert outcome.blocked is True


@pytest.mark.asyncio
async def test_fetch_caps_response_size() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * (5 * 1024 * 1024 + 1))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(make_source(), client=client, allow_private=True, **HERMETIC)
    assert outcome.status == "too_large"


def test_http_feed_requires_explicit_approval() -> None:
    assert validate_feed_url("http://example.com/feed", allow_http=False)
    assert validate_feed_url("http://example.com/feed", allow_http=True) == []


def test_private_literal_is_rejected() -> None:
    assert validate_feed_url("https://127.0.0.1/feed")
    assert validate_feed_url("https://[::1]/feed")
    assert validate_feed_url("https://10.0.0.5/feed")


# --- fetch-safety SPEC R2-R6, at the fetch boundary -------------------------

ROBOTS_HOST = "politeness-check.test"
FEED_URL = f"https://{ROBOTS_HOST}/feed.xml"


@pytest.mark.asyncio
async def test_fetch_robots_disallow_never_contacts_the_feed() -> None:
    seen: list[str] = []
    agent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        agent.append(request.headers.get("user-agent", ""))
        if request.url.path == "/robots.txt":
            return httpx.Response(
                200,
                content=b"User-agent: *\nDisallow: /\n",
                headers={"content-type": "text/plain"},
            )
        return httpx.Response(200, content=RSS, headers={"content-type": "application/rss+xml"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(
            make_source(feed_url=FEED_URL),
            client=client,
            allow_private=True,
            check_robots=True,
            ledger=HostLedger(mode="off"),
        )
    assert outcome.status == "robots_disallowed"
    assert outcome.blocked is True
    assert "/feed.xml" not in seen  # R2: a disallowing robots.txt means no request
    assert outcome.items == []
    assert all(a.startswith("HeraldFoxBot/") for a in agent)  # R1: the real identity


@pytest.mark.asyncio
async def test_fetch_429_honours_retry_after_as_a_cooldown() -> None:
    clock = {"now": 1_700_000_000.0}
    redis = FakeRedis()
    ledger = HostLedger(
        now=lambda: clock["now"], redis_factory=lambda: _as_redis(redis), mode="enforce"
    )

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"retry-after": "120"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(
            make_source(feed_url=FEED_URL),
            client=client,
            allow_private=True,
            check_robots=False,
            ledger=ledger,
        )
    assert outcome.status == "rate_limited"
    assert outcome.blocked is False  # transient: the source is not parked
    cooldowns = await ledger.cooldowns([ROBOTS_HOST])
    assert cooldowns[ROBOTS_HOST]["cooldown_reason"] == "rate_limited"
    assert cooldowns[ROBOTS_HOST]["cooldown_until"] >= clock["now"] + 120.0

    # And the next attempt inside the window is refused before it goes out.
    clock["now"] += 30.0
    decision = await ledger.decide(ROBOTS_HOST)
    assert decision.allowed is False
    assert decision.reason == "rate_limited"


@pytest.mark.asyncio
async def test_fetch_challenge_body_cools_the_host() -> None:
    clock = {"now": 1_700_000_000.0}
    redis = FakeRedis()
    ledger = HostLedger(
        now=lambda: clock["now"], redis_factory=lambda: _as_redis(redis), mode="enforce"
    )

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"<html><title>Just a moment...</title>Checking your browser</html>",
            headers={"content-type": "text/html"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(
            make_source(feed_url=FEED_URL),
            client=client,
            allow_private=True,
            check_robots=False,
            ledger=ledger,
        )
    assert outcome.status == "challenge"
    assert outcome.blocked is True
    assert outcome.items == []
    cooldowns = await ledger.cooldowns([ROBOTS_HOST])
    assert cooldowns[ROBOTS_HOST]["cooldown_reason"] == "challenge"


@pytest.mark.asyncio
async def test_fetch_tolerates_html_content_type_with_a_feed_body() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=RSS, headers={"content-type": "text/html"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(
            make_source(feed_url=FEED_URL), client=client, allow_private=True, **HERMETIC
        )
    assert outcome.status == "ok"  # the body decides, not the label
    assert outcome.items[0].title == "Regulator updates compliance rules"


@pytest.mark.asyncio
async def test_fetch_html_page_that_is_not_a_feed_is_blocked() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"<html><body><h1>Welcome to our news site</h1></body></html>",
            headers={"content-type": "text/html"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(
            make_source(feed_url=FEED_URL), client=client, allow_private=True, **HERMETIC
        )
    assert outcome.status == "blocked"
    assert outcome.blocked is True


@pytest.mark.asyncio
async def test_fetch_one_retry_on_a_dead_socket() -> None:
    attempts = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise httpx.ReadError("connection reset")
        return httpx.Response(200, content=RSS, headers={"content-type": "application/rss+xml"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(
            make_source(feed_url=FEED_URL), client=client, allow_private=True, **HERMETIC
        )
    assert outcome.status == "ok"
    assert attempts["n"] == 2  # exactly one retry, then success
