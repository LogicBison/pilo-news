from __future__ import annotations

import asyncio
import base64
import ipaddress
import os
import socket
from datetime import UTC
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx
import structlog

from news_api.articles.domain.models import FetchOutcome
from news_api.articles.infrastructure.normalize import parse_feed
from news_api.articles.infrastructure.politeness import (
    USER_AGENT,
    HostLedger,
    content_type_allowed,
    is_challenge,
    robots_allowed,
)
from news_api.platform.settings import get_settings
from news_api.sources.domain.models import Source
from news_api.sources.domain.validation import validate_feed_url

log = structlog.get_logger(__name__)

MAX_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 3
TIMEOUT = httpx.Timeout(12.0, connect=6.0)

# A dead socket is worth one more attempt; a `429` is worth none (SPEC R4/C4).
RETRYABLE = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadError,
    httpx.RemoteProtocolError,
)

# Re-exported: both fetchers present this identity (SPEC R1).
__all__ = [
    "MAX_BYTES",
    "MAX_REDIRECTS",
    "RETRYABLE",
    "TIMEOUT",
    "USER_AGENT",
    "fetch_source",
    "parse_retry_after",
    "validate_fetch_url",
]

_default_ledger: HostLedger | None = None


def get_ledger() -> HostLedger:
    """The process-wide host ledger (one Redis view per event loop)."""
    global _default_ledger
    if _default_ledger is None:
        _default_ledger = HostLedger()
    return _default_ledger


def parse_retry_after(value: str | None, *, now: float) -> float | None:
    """Seconds from now, for both forms a server may send (SPEC R4)."""
    if not value:
        return None
    raw = value.strip()
    if raw.isdigit():
        return float(raw)
    try:
        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return max(0.0, when.timestamp() - now)


async def _resolve_public_address(host: str, port: int) -> str | None:
    """First approved address for ``host``, or ``None`` when there is none.

    Every answer must be globally routable: one private record in the set is
    enough to reject the host, because httpx may pick any of them to connect.
    """
    if not host:
        return None
    loop = asyncio.get_running_loop()
    try:
        infos = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return None
    if not infos:
        return None
    for info in infos:
        address = info[4][0]
        try:
            parsed = ipaddress.ip_address(address)
        except ValueError:
            return None
        if not parsed.is_global:
            return None
    return infos[0][4][0]


async def _resolve_is_public(host: str, port: int) -> bool:
    return await _resolve_public_address(host, port) is not None


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


async def _pin_to_address(
    url: str, *, allow_http: bool, allow_private: bool
) -> tuple[str, dict[str, str], dict[str, object]]:
    """Validate ``url`` and return it pinned to the address we approved.

    Connecting to the literal IP closes the rebinding window between the check
    and the connect (SPEC R8): the socket goes where the validator looked. The
    ``Host`` header keeps the virtual host and ``sni_hostname`` keeps TLS
    certificate validation on the hostname. With ``allow_private`` (tests, or a
    deployment that opted in) there is nothing to pin, so the URL is untouched —
    but the literal-address and scheme rules still apply to every hop,
    redirect target included, exactly as before.
    """
    problems = validate_feed_url(url, allow_http=allow_http)
    if problems:
        raise ValueError("; ".join(problems))
    parts = urlsplit(url)
    host = parts.hostname or ""
    port = parts.port or (443 if parts.scheme == "https" else 80)
    default_port = 443 if parts.scheme == "https" else 80
    host_header = host if port == default_port else f"{host}:{port}"
    if allow_private:
        return url, {"Host": host_header}, {}

    address = await _resolve_public_address(host, port)
    if address is None:
        raise ValueError("feed host is not publicly routable")
    if address == host:
        return url, {"Host": host_header}, {}

    literal = f"[{address}]" if ":" in address and not address.startswith("[") else address
    netloc = literal if port == default_port else f"{literal}:{port}"
    pinned = urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    extensions: dict[str, object] = {}
    if parts.scheme == "https":
        extensions["sni_hostname"] = host
    return pinned, {"Host": host_header}, extensions


def _auth_headers(source: Source) -> dict[str, str]:
    """Per-source credentials, read from the environment at request time.

    The database stores only the *name* of the variable, so a leaked dump
    carries no credential. ``auth_type="header"`` sends the secret as the named
    header value — which is also how a publisher that asks for a specific
    ``User-Agent`` or a subscription token is honoured, without a global
    browser impersonation. ``basic`` sends ``user:password``.
    """
    if source.auth_type == "none":
        return {}
    reference = (source.auth_secret_ref or "").strip()
    if not reference:
        return {}
    secret = os.environ.get(reference, "").strip()
    if not secret:
        log.warning("ingest.auth_missing", source=source.name, secret_ref=reference)
        return {}
    if source.auth_type == "basic":
        token = base64.b64encode(secret.encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {token}"}
    return {(source.auth_header_name or "Authorization").strip(): secret}


async def _read_capped(response: httpx.Response) -> bytes:
    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > MAX_BYTES:
            raise ValueError("response too large")
        chunks.append(chunk)
    return b"".join(chunks)


def _outcome(
    source: Source, status: str, *, error: str | None = None, blocked: bool = False
) -> FetchOutcome:
    return FetchOutcome(source.id, source.name, status, [], error=error, blocked=blocked)


async def fetch_source(
    source: Source,
    *,
    client: httpx.AsyncClient | None = None,
    allow_private: bool | None = None,
    user_agent: str = USER_AGENT,
    ledger: HostLedger | None = None,
    check_robots: bool = True,
) -> FetchOutcome:
    """Fetch one source, politely: robots first, then pacing, then the request.

    Order matters. A disallowed or rate-limited host must not see a request at
    all, so both checks happen before the first byte goes out, and both return
    an outcome the run stats can count.
    """
    settings = get_settings()
    permit_private = settings.ssrf_allow_private if allow_private is None else allow_private
    host = urlsplit(source.feed_url).hostname or ""
    active = ledger or get_ledger()
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
    # A per-source header may replace the default identity when a publisher
    # asked for one; nothing here impersonates a browser by default.
    headers.update(_auth_headers(source))

    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False)
    url = source.feed_url
    retry_after: float | None = None
    try:
        # R2 — robots before anything else: a disallowing document means the
        # feed itself is never contacted.
        crawl_delay = 0.0
        if check_robots:
            allowed, crawl_delay = await robots_allowed(
                url,
                user_agent=user_agent,
                client=http,
                validator=lambda candidate: validate_fetch_url(
                    candidate, allow_http=source.allow_http, allow_private=permit_private
                ),
            )
            if not allowed:
                log.info("ingest.robots_disallowed", source=source.name, host=host)
                return _outcome(
                    source,
                    "robots_disallowed",
                    error="robots.txt disallows this path",
                    blocked=True,
                )

        # R3 — per-host floor, hourly cap, cooldown and breaker.
        decision = await active.decide(host, crawl_delay=crawl_delay)
        if not decision.allowed:
            log.info(
                "ingest.paced_out",
                source=source.name,
                host=host,
                reason=decision.reason,
                wait_s=round(decision.wait_s, 1),
            )
            return _outcome(
                source,
                "rate_limited",
                error=f"{decision.reason}: retry in {int(decision.wait_s)}s",
            )

        attempt = 0
        redirects = 0
        while True:
            try:
                request_url, host_headers, extensions = await _pin_to_address(
                    url, allow_http=source.allow_http, allow_private=permit_private
                )
                async with http.stream(
                    "GET",
                    request_url,
                    headers={**headers, **host_headers},
                    extensions=extensions,
                ) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("location")
                        if not location:
                            await active.record(host, "http_5xx")
                            return _outcome(source, "http_error", error="redirect without location")
                        if redirects >= MAX_REDIRECTS:
                            return _outcome(source, "http_error", error="too many redirects")
                        redirects += 1
                        url = urljoin(url, location)
                        continue
                    if response.status_code == 304:
                        await active.record(host, "http_304")
                        return FetchOutcome(
                            source.id,
                            source.name,
                            "http_304",
                            [],
                            etag=response.headers.get("etag") or source.etag,
                            last_modified=response.headers.get("last-modified")
                            or source.last_modified,
                        )
                    if response.status_code == 429 or response.status_code == 503:
                        # R4 — the server asked for a pause; we honour it and do
                        # not come back inside the window.
                        retry_after = parse_retry_after(
                            response.headers.get("retry-after"), now=active_now(active)
                        )
                        await active.record(host, "rate_limited", retry_after=retry_after)
                        wait = int(retry_after or 0)
                        return _outcome(
                            source,
                            "rate_limited",
                            error=f"http {response.status_code}"
                            + (f", retry after {wait}s" if wait else ""),
                        )
                    if response.status_code in (401, 403):
                        # A refusal is either a WAF challenge wearing a 403 or
                        # a real "no". Both stop here; only one is worth
                        # retrying in an hour.
                        body = await _read_capped(response)
                        if is_challenge(body):
                            await active.record(host, "challenge")
                            log.warning(
                                "ingest.challenge",
                                source=source.name,
                                host=host,
                                status=response.status_code,
                            )
                            return _outcome(
                                source,
                                "challenge",
                                error="anti-bot challenge page",
                                blocked=True,
                            )
                        await active.record(host, "denied")
                        log.warning(
                            "ingest.denied",
                            source=source.name,
                            host=host,
                            status=response.status_code,
                        )
                        return _outcome(
                            source,
                            "denied",
                            error=f"http {response.status_code}: publisher refused access",
                            blocked=True,
                        )
                    if response.status_code >= 400:
                        if 400 <= response.status_code < 500 and response.status_code != 408:
                            await active.record(host, "http_4xx")
                        else:
                            await active.record(host, "http_5xx")
                        return _outcome(source, "http_error", error=f"http {response.status_code}")

                    body = await _read_capped(response)
                    declared = response.headers.get("content-type")
                    if not content_type_allowed(declared):
                        # R6/C5 — a challenge body is never parsed and never
                        # retried in a hurry.
                        if is_challenge(body):
                            await active.record(host, "challenge")
                            log.warning(
                                "ingest.challenge",
                                source=source.name,
                                host=host,
                                content_type=declared,
                            )
                            return _outcome(
                                source,
                                "challenge",
                                error="anti-bot challenge page",
                                blocked=True,
                            )
                        # A mislabelled feed still parses; a page does not.
                        items = _parse_lenient(body, source)
                        if not items:
                            await active.record(host, "http_5xx")
                            return _outcome(
                                source,
                                "blocked",
                                error=f"unexpected content-type {declared or 'none'}",
                                blocked=True,
                            )
                        await active.record(host, "ok")
                        return FetchOutcome(
                            source.id,
                            source.name,
                            "ok",
                            items,
                            etag=response.headers.get("etag"),
                            last_modified=response.headers.get("last-modified"),
                        )
                    items = parse_feed(body, source_name=source.name, language=source.language)
                    await active.record(host, "ok")
                    return FetchOutcome(
                        source.id,
                        source.name,
                        "ok",
                        items,
                        etag=response.headers.get("etag"),
                        last_modified=response.headers.get("last-modified"),
                    )
            except RETRYABLE:
                attempt += 1
                if attempt > 1:
                    raise
                # One retry for a dead socket, and only for that.
                log.info("ingest.fetch_retry", source=source.name, host=host, attempt=attempt)
    except ValueError as exc:
        message = str(exc)
        blocked = (
            "not publicly routable" in message
            or "public address" in message
            or "must use https" in message
            or "require allow_http" in message
            or "unexpected content-type" in message
        )
        status = (
            "too_large" if "too large" in message else ("blocked" if blocked else "parse_error")
        )
        log.warning("ingest.fetch_rejected", source=source.name, reason=message[:120])
        return FetchOutcome(
            source.id, source.name, status, [], error=message[:200], blocked=blocked
        )
    except (TimeoutError, httpx.TimeoutException):
        await _quiet_record(active, host, "timeout")
        return FetchOutcome(source.id, source.name, "timeout", [], error="timeout")
    except httpx.HTTPError as exc:
        await _quiet_record(active, host, "http_error")
        return FetchOutcome(source.id, source.name, "http_error", [], error=type(exc).__name__)
    except Exception as exc:  # pragma: no cover - parser/upstream corner
        log.warning("ingest.fetch_failed", source=source.name, error=type(exc).__name__)
        return FetchOutcome(source.id, source.name, "parse_error", [], error=type(exc).__name__)
    finally:
        if owns_client:
            await http.aclose()


def active_now(ledger: HostLedger) -> float:
    """The ledger's clock, so ``Retry-After`` is measured against the same one."""
    return ledger.now()


async def _quiet_record(ledger: HostLedger, host: str, outcome: str) -> None:
    """Record a transport failure without letting metrics break the fetch."""
    try:
        await ledger.record(host, outcome)
    except Exception:  # pragma: no cover - ledger never raises, belt and braces
        pass


def _parse_lenient(body: bytes, source: Source):
    """Items from a body whose Content-Type we do not trust, else ``None``."""
    try:
        items = parse_feed(body, source_name=source.name, language=source.language)
    except Exception:
        return None
    return items or None
