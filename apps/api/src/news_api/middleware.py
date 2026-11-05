from __future__ import annotations

import re
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from news_api.platform.logging import get_logger, request_id_var
from news_api.platform.metrics import HTTP_DURATION, HTTP_REQUESTS
from news_api.platform.settings import get_settings

log = get_logger(__name__)
REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{8,64}$")

Handler = Callable[[Request], Awaitable[Response]]


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        incoming = request.headers.get("x-request-id")
        request_id = incoming if incoming and REQUEST_ID_RE.match(incoming) else uuid.uuid4().hex
        request.state.request_id = request_id
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log.exception("request.error", route=request.url.path, method=request.method)
            raise
        finally:
            request_id_var.reset(token)

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-Id"] = request_id
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        if get_settings().app_env == "prd":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        if response.headers.get("content-type", "").startswith("text/html"):
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; frame-ancestors 'none'",
            )
        for key, value in getattr(request.state, "rate_limit_headers", {}).items():
            response.headers.setdefault(key, value)
        if "server" in response.headers:
            del response.headers["server"]

        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        status_class = f"{response.status_code // 100}xx"
        HTTP_REQUESTS.labels(
            route=route_path, method=request.method, status_class=status_class
        ).inc()
        HTTP_DURATION.labels(route=route_path, method=request.method).observe(duration_ms / 1000)
        log.info(
            "request.end",
            route=route_path,
            method=request.method,
            status=response.status_code,
            duration_ms=duration_ms,
            industry=request.path_params.get("industry"),
            locale=request.query_params.get("locale"),
        )
        return response
