from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit, urlunsplit

BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal", "metadata"}


def normalize_feed_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower().rstrip(".")
    scheme = parts.scheme.lower()
    if not scheme or not host:
        return url.strip()
    port = parts.port
    netloc = host
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{host}:{port}"
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def is_private_literal(host: str) -> bool:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return not address.is_global


def validate_feed_url(url: str, *, allow_http: bool = False) -> list[str]:
    problems: list[str] = []
    if not url or len(url) > 2048:
        return ["feed_url must be a URL under 2048 characters"]
    parts = urlsplit(url)
    if parts.scheme not in ("https", "http"):
        problems.append("feed_url must use https (http requires allow_http=true)")
    elif parts.scheme == "http" and not allow_http:
        problems.append("http feeds require allow_http=true")
    if not parts.hostname:
        problems.append("feed_url must include a host")
    if parts.username or parts.password:
        problems.append("feed_url must not contain credentials")
    host = (parts.hostname or "").lower()
    if host in BLOCKED_HOSTNAMES or host.endswith(".local") or host.endswith(".internal"):
        problems.append("feed_url host is not publicly routable")
    if is_private_literal(host):
        problems.append("feed_url host must be a public address")
    return problems
