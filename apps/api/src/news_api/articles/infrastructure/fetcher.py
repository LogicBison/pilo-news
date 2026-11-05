from __future__ import annotations

import asyncio
import ipaddress
import socket
from urllib.parse import urljoin, urlsplit

import httpx
import structlog

from news_api.articles.domain.models import FetchOutcome
from news_api.articles.infrastructure.normalize import parse_feed
from news_api.platform.settings import get_settings
from news_api.sources.domain.models import Source
from news_api.sources.domain.validation import validate_feed_url

log = structlog.get_logger(__name__)

MAX_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 3
TIMEOUT = httpx.Timeout(12.0, connect=6.0)
USER_AGENT = "SystemNewsBot/1.0 (+https://system-news.example/bot)"


async def _resolve_is_public(host: str, port: int) -> bool:
    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    if not infos:
        return False
    for info in infos:
        address = info[4][0]
        try:
            parsed = ipaddress.ip_address(address)
        except ValueError:
            return False
        if not parsed.is_global:
            return False
    return True


async def validate_fetch_url(
    url: str, *, allow_http: bool = False, allow_private: bool = False
) -> str:
    problems = validate_feed_url(url, allow_http=allow_http)
    if problems:
        raise ValueError("; ".join(problems))
    parts = urlsplit(url)
    if not allow_private and not await _resolve_is_public(
        parts.hostname or "", parts.port or (443 if parts.scheme == "https" else 80)
    ):
        raise ValueError("feed host is not publicly routable")
    return url


async def _read_capped(response: httpx.Response) -> bytes:
    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > MAX_BYTES:
            raise ValueError("response too large")
        chunks.append(chunk)
    return b"".join(chunks)


async def fetch_source(
    source: Source,
    *,
    client: httpx.AsyncClient | None = None,
    allow_private: bool | None = None,
    user_agent: str = USER_AGENT,
) -> FetchOutcome:
    settings = get_settings()
    permit_private = settings.ssrf_allow_private if allow_private is None else allow_private
    headers = {
        "User-Agent": user_agent,
        "Accept": (
            "application/rss+xml, application/atom+xml, application/xml, "
            "text/xml;q=0.9, */*;q=0.1"
        ),
    }
    if source.etag:
        headers["If-None-Match"] = source.etag
    if source.last_modified:
        headers["If-Modified-Since"] = source.last_modified

    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False)
    url = source.feed_url
    try:
        for _ in range(MAX_REDIRECTS + 1):
            await validate_fetch_url(
                url, allow_http=source.allow_http, allow_private=permit_private
            )
            async with http.stream("GET", url, headers=headers) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        return FetchOutcome(
                            source.id,
                            source.name,
                            "http_error",
                            [],
                            error="redirect without location",
                        )
                    url = urljoin(url, location)
                    continue
                if response.status_code == 304:
                    return FetchOutcome(
                        source.id,
                        source.name,
                        "http_304",
                        [],
                        etag=response.headers.get("etag") or source.etag,
                        last_modified=response.headers.get("last-modified") or source.last_modified,
                    )
                if response.status_code >= 400:
                    return FetchOutcome(
                        source.id,
                        source.name,
                        "http_error",
                        [],
                        error=f"http {response.status_code}",
                    )
                body = await _read_capped(response)
                items = parse_feed(body, source_name=source.name, language=source.language)
                return FetchOutcome(
                    source.id,
                    source.name,
                    "ok",
                    items,
                    etag=response.headers.get("etag"),
                    last_modified=response.headers.get("last-modified"),
                )
        return FetchOutcome(source.id, source.name, "http_error", [], error="too many redirects")
    except ValueError as exc:
        message = str(exc)
        blocked = (
            "not publicly routable" in message
            or "public address" in message
            or "must use https" in message
            or "require allow_http" in message
        )
        status = (
            "too_large" if "too large" in message else ("blocked" if blocked else "parse_error")
        )
        log.warning("ingest.fetch_rejected", source=source.name, reason=message[:120])
        return FetchOutcome(
            source.id, source.name, status, [], error=message[:200], blocked=blocked
        )
    except (TimeoutError, httpx.TimeoutException):
        return FetchOutcome(source.id, source.name, "timeout", [], error="timeout")
    except httpx.HTTPError as exc:
        return FetchOutcome(source.id, source.name, "http_error", [], error=type(exc).__name__)
    except Exception as exc:  # pragma: no cover - parser/upstream corner
        log.warning("ingest.fetch_failed", source=source.name, error=type(exc).__name__)
        return FetchOutcome(source.id, source.name, "parse_error", [], error=type(exc).__name__)
    finally:
        if owns_client:
            await http.aclose()
