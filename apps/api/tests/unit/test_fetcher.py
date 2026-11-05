import httpx
import pytest

from news_api.articles.infrastructure.fetcher import fetch_source
from news_api.sources.domain.models import Source
from news_api.sources.domain.validation import validate_feed_url


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
        outcome = await fetch_source(make_source(etag='"old"'), client=client, allow_private=True)
    assert outcome.status == "ok"
    assert outcome.items[0].title == "Regulator updates compliance rules"
    assert seen["if_none_match"] == '"old"'


@pytest.mark.asyncio
async def test_fetch_304_is_success_without_parsing() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(304, headers={"etag": '"same"'})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(make_source(), client=client, allow_private=True)
    assert outcome.status == "http_304"
    assert outcome.items == []


@pytest.mark.asyncio
async def test_fetch_blocks_redirect_to_metadata() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://169.254.169.254/latest/meta-data"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(make_source(), client=client, allow_private=True)
    assert outcome.status == "blocked"
    assert outcome.blocked is True


@pytest.mark.asyncio
async def test_fetch_caps_response_size() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * (5 * 1024 * 1024 + 1))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        outcome = await fetch_source(make_source(), client=client, allow_private=True)
    assert outcome.status == "too_large"


def test_http_feed_requires_explicit_approval() -> None:
    assert validate_feed_url("http://example.com/feed", allow_http=False)
    assert validate_feed_url("http://example.com/feed", allow_http=True) == []


def test_private_literal_is_rejected() -> None:
    assert validate_feed_url("https://127.0.0.1/feed")
    assert validate_feed_url("https://[::1]/feed")
    assert validate_feed_url("https://10.0.0.5/feed")
