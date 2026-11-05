from __future__ import annotations

from typing import Any

from fastapi import Request

from news_api.platform.cache import get_redis
from news_api.platform.clock import utcnow
from news_api.platform.errors import SessionExpired, Unauthorized
from news_api.platform.security import decode_admin_token

DENYLIST_PREFIX = "session:denied:"


def operator_from_token(token: str | None) -> dict[str, Any]:
    if not token:
        raise Unauthorized("Admin authentication required.")
    try:
        payload = decode_admin_token(token)
    except Exception as exc:
        raise SessionExpired("Session is invalid or expired.") from exc
    return {
        "id": str(payload["sub"]),
        "email": str(payload.get("email") or ""),
        "jti": str(payload["jti"]),
        "exp": int(payload["exp"]),
    }


async def ensure_not_denied(jti: str) -> None:
    try:
        client = await get_redis()
        if await client.exists(f"{DENYLIST_PREFIX}{jti}"):
            raise SessionExpired("Session has been logged out.")
    except SessionExpired:
        raise
    except Exception:
        return


async def deny_token(jti: str, exp: int) -> None:
    ttl = max(60, exp - int(utcnow().timestamp()) + 30)
    try:
        client = await get_redis()
        await client.set(f"{DENYLIST_PREFIX}{jti}", "1", ex=ttl)
    except Exception:
        return


def token_from_request(request: Request) -> str | None:
    cookie = request.cookies.get("sn_admin")
    if cookie:
        return cookie
    header = request.headers.get("authorization")
    if header and header.lower().startswith("bearer "):
        return header[7:].strip()
    return None


async def current_operator(request: Request) -> dict[str, Any]:
    cached = getattr(request.state, "operator", None)
    if cached:
        return cached
    operator = operator_from_token(token_from_request(request))
    await ensure_not_denied(operator["jti"])
    request.state.operator = operator
    return operator


def require_csrf(request: Request) -> None:
    from news_api.platform.errors import CSRFInvalid
    from news_api.platform.security import constant_eq

    cookie = request.cookies.get("sn_csrf")
    header = request.headers.get("x-csrf-token")
    if not cookie or not header or not constant_eq(cookie, header):
        raise CSRFInvalid("CSRF token is missing or invalid.")
