"""Shared test bootstrap: isolated database, migrations, and cleanup."""

from __future__ import annotations

import asyncio
import os
from urllib.parse import quote_plus

import asyncpg
import pytest

POSTGRES_USER = os.environ.get("POSTGRES_USER", "news")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "change-me")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.environ.get("TEST_POSTGRES_PORT", "5432")
TEST_DB = os.environ.get("POSTGRES_TEST_DB", "news_test")

os.environ["APP_ENV"] = "test"
_base_redis = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
os.environ["REDIS_URL"] = os.environ.get("TEST_REDIS_URL") or _base_redis.rsplit("/", 1)[0] + "/1"
os.environ["SECRET_KEY"] = "test-secret-key-for-system-news"
os.environ["DATABASE_URL"] = (
    f"postgresql+asyncpg://{quote_plus(POSTGRES_USER)}:{quote_plus(POSTGRES_PASSWORD)}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{TEST_DB}"
)
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "test-admin-password"
os.environ["AI_ENABLED"] = "false"
os.environ["METRICS_ENABLED"] = "true"


async def _ensure_database() -> None:
    dsn = (
        f"postgresql://{quote_plus(POSTGRES_USER)}:{quote_plus(POSTGRES_PASSWORD)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
    )
    connection = await asyncpg.connect(dsn)
    try:
        exists = await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB)
        if not exists:
            await connection.execute(f'CREATE DATABASE "{TEST_DB}"')
    finally:
        await connection.close()


@pytest.fixture(scope="session")
def prepared_db():
    from news_api.platform.db import dispose
    from news_api.platform.migrations import run_migrations

    asyncio.run(_ensure_database())
    asyncio.run(run_migrations())
    asyncio.run(dispose())
    yield


async def _truncate() -> None:
    from sqlalchemy import text

    from news_api.platform.cache import get_redis
    from news_api.platform.db import engine

    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE articles, pins, refresh_runs, audit_events, leads, "
                "lead_events, contact_messages, cta_events, api_keys, offer_issues CASCADE"
            )
        )
        await conn.execute(text("UPDATE industries SET enabled = TRUE"))
        await conn.execute(
            text(
                "UPDATE industries SET fetch_interval_minutes = NULL, "
                "auto_fetch_enabled = TRUE, offers = '{}'::jsonb"
            )
        )
        await conn.execute(text("UPDATE partners SET status = 'active'"))
        await conn.execute(text("DELETE FROM sources WHERE feed_url LIKE 'https://example.org/%'"))
        await conn.execute(text("DELETE FROM industries WHERE slug LIKE 'e2e-%'"))
        await conn.execute(text("UPDATE sources SET enabled = TRUE, status = 'active'"))
    try:
        redis = await get_redis()
        await redis.flushdb()
    except Exception:
        pass


@pytest.fixture
async def clean_db(prepared_db):
    await _truncate()
    yield
    await _truncate()


@pytest.fixture
async def client(clean_db):
    import httpx

    from news_api.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.fixture
async def admin_client(client):
    from news_api.platform.security import create_admin_token

    token, _ = create_admin_token("operator", "admin@example.com")
    csrf = "test-csrf-token"
    client.cookies.set("sn_admin", token)
    client.cookies.set("sn_csrf", csrf)
    client.headers["x-csrf-token"] = csrf
    return client
