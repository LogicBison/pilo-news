from __future__ import annotations

import hashlib
import json
from typing import Any

from fastapi import Request
from fastapi.responses import Response

PUBLIC_CACHE = "public, max-age=60, stale-while-revalidate=300"
NO_STORE = "no-store"


def json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, default=str, sort_keys=True, separators=(",", ":")).encode("utf-8")


VOLATILE_KEYS = {"generated_at", "request_id"}


def _stable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _stable(item) for key, item in value.items() if key not in VOLATILE_KEYS}
    if isinstance(value, list):
        return [_stable(item) for item in value]
    return value


def render_json(
    request: Request,
    payload: Any,
    *,
    status: int = 200,
    cache_control: str = PUBLIC_CACHE,
    extra_headers: dict[str, str] | None = None,
) -> Response:
    body = json_bytes(payload)
    etag = 'W/"' + hashlib.sha256(json_bytes(_stable(payload))).hexdigest()[:32] + '"'
    headers = {"ETag": etag, "Cache-Control": cache_control}
    if extra_headers:
        headers.update(extra_headers)
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(
        content=body,
        status_code=status,
        headers=headers,
        media_type="application/json; charset=utf-8",
    )
