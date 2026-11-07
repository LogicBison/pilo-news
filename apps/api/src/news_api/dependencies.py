from __future__ import annotations

from typing import Any

from fastapi import Request

from news_api.editorial.application.auth import current_operator, require_csrf
from news_api.editorial.infrastructure.repo import find_api_key, touch_api_key
from news_api.platform.cache import get_redis, rate_limit
from news_api.platform.errors import Forbidden, InvalidKey, RateLimited
from news_api.platform.metrics import RATE_LIMITED
from news_api.platform.security import hash_api_key
from news_api.platform.settings import get_settings


def client_country(request: Request) -> str:
    """Country from a trusted edge header; empty until the operator configures one."""
    header = get_settings().geo_country_header.strip().lower()
    if not header:
        return ""
    value = request.headers.get(header, "").strip().upper()
    if len(value) == 2 and value.isalpha():
        return value
    return ""


def request_id_of(request: Request) -> str:
    return str(getattr(request.state, "request_id", "-"))


def client_ip(request: Request) -> str:
    settings = get_settings()
    if settings.trust_forwarded_for:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip() or "unknown"
    return request.client.host if request.client else "unknown"


def reject_unknown_query(request: Request, allowed: set[str]) -> None:
    from news_api.platform.errors import InvalidQuery

    unknown = sorted(set(request.query_params.keys()) - allowed)
    if unknown:
        raise InvalidQuery(f"Unknown query parameter(s): {', '.join(unknown)}.")


def _rate_headers(limit: int, remaining: int, reset: int) -> dict[str, str]:
    return {
        "RateLimit-Limit": str(limit),
        "RateLimit-Remaining": str(max(0, remaining)),
        "RateLimit-Reset": str(reset),
    }


async def enforce_rate_limit(
    request: Request,
    *,
    scope: str,
    identity: str,
    limit: int,
    window_seconds: int,
) -> None:
    allowed, remaining, reset = await rate_limit(f"{scope}:{identity}", limit, window_seconds)
    headers = _rate_headers(limit, remaining, reset)
    request.state.rate_limit_headers = headers
    if not allowed:
        RATE_LIMITED.labels(scope=scope).inc()
        headers["Retry-After"] = str(max(1, reset - int(__import__("time").time())))
        raise RateLimited("Too many requests. Try again later.", headers=headers)


async def resolve_api_key(request: Request) -> dict[str, Any] | None:
    raw = request.headers.get("x-api-key")
    if not raw:
        return None
    if not raw.startswith("sn_live_"):
        raise InvalidKey("API key is invalid.")
    key = await find_api_key(hash_api_key(raw))
    if not key or not key.get("enabled"):
        raise InvalidKey("API key is invalid.")
    scopes = list(key.get("scopes") or [])
    if "read" not in scopes:
        raise Forbidden("API key lacks the read scope.")
    try:
        client = await get_redis()
        first_use = await client.set(f"api_key:touch:{key['id']}", "1", nx=True, ex=60)
        if first_use:
            await touch_api_key(str(key["id"]))
    except Exception:
        pass
    request.state.api_key = key
    return key


async def public_access(request: Request) -> dict[str, Any] | None:
    settings = get_settings()
    key = await resolve_api_key(request)
    if key:
        limit = min(int(key.get("rate_limit") or settings.rate_limit_keyed), 10_000)
        await enforce_rate_limit(
            request,
            scope="key",
            identity=str(key["id"]),
            limit=limit,
            window_seconds=60,
        )
    else:
        await enforce_rate_limit(
            request,
            scope="ip",
            identity=client_ip(request),
            limit=settings.rate_limit_keyless,
            window_seconds=60,
        )
    return key


async def admin_auth(request: Request) -> dict[str, Any]:
    operator = await current_operator(request)
    settings = get_settings()
    await enforce_rate_limit(
        request,
        scope="admin",
        identity=f"{client_ip(request)}:{operator['id']}",
        limit=max(settings.rate_limit_keyed, 600),
        window_seconds=60,
    )
    return operator


async def admin_mutation(request: Request) -> dict[str, Any]:
    operator = await admin_auth(request)
    require_csrf(request)
    return operator
