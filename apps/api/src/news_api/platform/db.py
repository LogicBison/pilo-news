from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from news_api.platform.settings import get_settings

_settings = get_settings()

if _settings.app_env == "test":
    engine: AsyncEngine = create_async_engine(
        _settings.database_url,
        pool_pre_ping=False,
        poolclass=NullPool,
    )
else:
    engine = create_async_engine(
        _settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=5,
        pool_timeout=10,
    )
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Params = Mapping[str, Any] | None


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: one session per request."""
    async with SessionLocal() as session:
        yield session


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def fetch_all(sql: str, params: Params = None) -> list[dict[str, Any]]:
    async with session_scope() as session:
        result = await session.execute(text(sql), dict(params or {}))
        return [dict(row) for row in result.mappings().all()]


async def fetch_one(sql: str, params: Params = None) -> dict[str, Any] | None:
    rows = await fetch_all(sql, params)
    return rows[0] if rows else None


async def execute(sql: str, params: Params = None) -> int:
    async with session_scope() as session:
        result = await session.execute(text(sql), dict(params or {}))
        return int(getattr(result, "rowcount", 0) or 0)


async def dispose() -> None:
    await engine.dispose()
