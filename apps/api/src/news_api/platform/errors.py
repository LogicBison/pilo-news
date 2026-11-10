from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from news_api.platform.logging import get_logger

log = get_logger(__name__)

PROBLEM_BASE = "https://heraldfox.com/problems"


class DomainError(Exception):
    status = 400
    code = "bad-request"
    title = "Bad Request"

    def __init__(self, detail: str, *, headers: dict[str, str] | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        self.headers = headers or {}


class InvalidQuery(DomainError):
    status = 400
    code = "invalid-query"
    title = "Invalid Query"


class InvalidCursor(DomainError):
    status = 400
    code = "invalid-cursor"
    title = "Invalid Cursor"


class InvalidLocale(DomainError):
    status = 400
    code = "invalid-locale"
    title = "Invalid Locale"


class Unauthorized(DomainError):
    status = 401
    code = "unauthorized"
    title = "Unauthorized"


class InvalidKey(DomainError):
    status = 401
    code = "invalid-key"
    title = "Invalid API Key"


class SessionExpired(DomainError):
    status = 401
    code = "session-expired"
    title = "Session Expired"


class Forbidden(DomainError):
    status = 403
    code = "forbidden"
    title = "Forbidden"


class CSRFInvalid(DomainError):
    status = 403
    code = "csrf-invalid"
    title = "CSRF Check Failed"


class NotFound(DomainError):
    status = 404
    code = "not-found"
    title = "Not Found"


class Conflict(DomainError):
    status = 409
    code = "conflict"
    title = "Conflict"


class RefreshInProgress(Conflict):
    code = "refresh-in-progress"
    title = "Refresh In Progress"


class ValidationProblem(DomainError):
    status = 422
    code = "validation"
    title = "Validation Failed"


class ConsentRequired(ValidationProblem):
    code = "consent-required"
    title = "Consent Required"


class RateLimited(DomainError):
    status = 429
    code = "rate-limited"
    title = "Rate Limited"


class UpstreamError(DomainError):
    status = 502
    code = "upstream-error"
    title = "Upstream Error"


class DependencyUnavailable(DomainError):
    status = 503
    code = "dependency-unavailable"
    title = "Dependency Unavailable"


def request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def problem(
    request: Request,
    *,
    status: int,
    code: str,
    title: str,
    detail: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = {
        "type": f"{PROBLEM_BASE}/{code}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "request_id": request_id(request),
    }
    return JSONResponse(body, status_code=status, headers=headers)


def register_exception_handlers(app: Any) -> None:
    @app.exception_handler(DomainError)
    async def _domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return problem(
            request,
            status=exc.status,
            code=exc.code,
            title=exc.title,
            detail=exc.detail,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        fields = []
        for error in exc.errors()[:10]:
            location = ".".join(str(part) for part in error.get("loc", ()) if part != "body")
            fields.append(
                {"field": location or "body", "message": str(error.get("msg", "invalid"))}
            )
        return problem(
            request,
            status=422,
            code="validation",
            title="Validation Failed",
            detail="Request validation failed.",
            headers={"X-Validation-Fields": str(len(fields))},
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {
            400: "bad-request",
            401: "unauthorized",
            403: "forbidden",
            404: "not-found",
            405: "method-not-allowed",
            409: "conflict",
            429: "rate-limited",
        }.get(exc.status_code, "http-error")
        return problem(
            request,
            status=exc.status_code,
            code=code,
            title=str(exc.detail) if exc.detail else "HTTP Error",
            detail=str(exc.detail) if exc.detail else "Request failed.",
            headers=dict(exc.headers or {}),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.error("request.unhandled", error=type(exc).__name__, route=request.url.path)
        return problem(
            request,
            status=500,
            code="internal-error",
            title="Internal Server Error",
            detail="An unexpected error occurred.",
        )
