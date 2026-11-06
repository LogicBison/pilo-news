from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from news_api.channels.http.routes import router as industries_router
from news_api.editorial.http.api_keys import router as api_keys_router
from news_api.editorial.http.audit import router as audit_router
from news_api.editorial.http.auth import router as auth_router
from news_api.editorial.http.industries import router as admin_industries_router
from news_api.editorial.http.leads import router as admin_leads_router
from news_api.editorial.http.moderation import router as moderation_router
from news_api.editorial.http.refresh import router as refresh_router
from news_api.editorial.http.sources import router as admin_sources_router
from news_api.editorial.http.topics import router as admin_topics_router
from news_api.middleware import RequestContextMiddleware
from news_api.offers.http.routes import router as admin_offers_router
from news_api.platform.cache import close_redis, ping
from news_api.platform.db import dispose, fetch_one
from news_api.platform.errors import register_exception_handlers
from news_api.platform.logging import configure_logging, get_logger
from news_api.platform.metrics import metrics_enabled, metrics_payload
from news_api.platform.migrations import migrations_applied, run_migrations
from news_api.platform.settings import get_settings
from news_api.publishing.http.contact import router as contact_router
from news_api.publishing.http.cta import router as cta_router
from news_api.publishing.http.funnel import router as funnel_router
from news_api.publishing.http.leads import router as leads_router
from news_api.publishing.http.news import router as news_router
from news_api.publishing.http.taxonomy import router as taxonomy_router

settings = get_settings()
configure_logging(settings.log_level, settings.log_json)
log = get_logger(__name__)

VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> Any:
    log.info("api.start", env=settings.app_env, version=VERSION)
    if settings.run_migrations:
        try:
            await run_migrations()
        except Exception as exc:
            log.error("migrations.startup_failed", error=type(exc).__name__)
            raise
    yield
    await close_redis()
    await dispose()
    log.info("api.stop")


app = FastAPI(
    title="System News API",
    version=VERSION,
    description="Bilingual industry news API. Public reads need no key.",
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
    expose_headers=["ETag", "X-Request-Id", "RateLimit-Limit", "RateLimit-Remaining"],
)
app.add_middleware(RequestContextMiddleware)
register_exception_handlers(app)


@app.get("/v1/health", tags=["system"])
async def health() -> Any:
    checks: dict[str, Any] = {"db": False, "redis": False, "migrations": False}
    try:
        row = await fetch_one("SELECT 1 AS ok")
        checks["db"] = bool(row and row.get("ok") == 1)
    except Exception:
        checks["db"] = False
    checks["redis"] = await ping()
    checks["migrations"] = await migrations_applied()
    healthy = checks["db"] and checks["migrations"]
    body = {
        "status": "ok" if healthy and checks["redis"] else ("degraded" if healthy else "error"),
        "service": "api",
        "env": settings.app_env,
        "version": VERSION,
        "checks": checks,
    }
    return JSONResponse(
        body,
        status_code=200 if healthy else 503,
        headers={"Cache-Control": "no-store"},
    )


@app.get("/v1/health/ready", tags=["system"])
async def readiness() -> Any:
    checks: dict[str, Any] = {
        "db": False,
        "redis": await ping(),
        "migrations": await migrations_applied(),
    }
    try:
        row = await fetch_one("SELECT 1 AS ok")
        checks["db"] = bool(row and row.get("ok") == 1)
    except Exception:
        pass
    ready = all(checks.values())
    return JSONResponse(
        {"status": "ready" if ready else "not-ready", "checks": checks},
        status_code=200 if ready else 503,
        headers={"Cache-Control": "no-store"},
    )


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    if not metrics_enabled():
        return Response(status_code=404)
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)


@app.get("/", include_in_schema=False)
async def root() -> Any:
    return {"service": "system-news-api", "version": VERSION, "docs": "/v1/docs"}


app.include_router(industries_router)
app.include_router(news_router)
app.include_router(taxonomy_router)
app.include_router(contact_router)
app.include_router(leads_router)
app.include_router(cta_router)
app.include_router(auth_router)
app.include_router(admin_sources_router)
app.include_router(admin_topics_router)
app.include_router(moderation_router)
app.include_router(refresh_router)
app.include_router(api_keys_router)
app.include_router(audit_router)
app.include_router(admin_industries_router)
app.include_router(admin_leads_router)
app.include_router(funnel_router)
app.include_router(admin_offers_router)
