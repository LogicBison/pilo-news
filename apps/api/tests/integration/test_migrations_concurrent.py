"""Two backends migrate at boot; the second must wait, not crash.

`compose up` starts the api and the worker together and both call
``run_migrations()``. Without a lock they race on the same ``CREATE TABLE`` and
Postgres answers with a unique violation on ``pg_type`` - ``IF NOT EXISTS`` does
not help, because both statements check before either commits. The loser used to
die on the first boot after any new migration; ``restart: unless-stopped`` hid it
as a one-cycle crash. This test runs the real scripts against a throwaway
database, so it fails if the advisory lock is ever removed.
"""

from __future__ import annotations

import asyncio
import uuid

import asyncpg
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from news_api.platform import migrations as module
from news_api.platform.settings import get_settings

CONCURRENT = 4


def _dsn(database: str) -> str:
    return get_settings().database_url.rpartition("/")[0] + "/" + database


def _asyncpg_dsn(database: str) -> str:
    return _dsn(database).replace("postgresql+asyncpg://", "postgresql://", 1)


@pytest.mark.asyncio
async def test_concurrent_migrations_apply_once_and_neither_backend_crashes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    name = f"news_mig_race_{uuid.uuid4().hex[:8]}"
    admin = await asyncpg.connect(_asyncpg_dsn("postgres"))
    try:
        await admin.execute(f'CREATE DATABASE "{name}"')
    finally:
        await admin.close()

    engine = create_async_engine(_dsn(name), poolclass=NullPool)
    monkeypatch.setattr(module, "engine", engine)
    expected = {path.name for path in module.MIGRATIONS_DIR.glob("*.sql")}
    try:
        results = await asyncio.gather(
            *(module.run_migrations() for _ in range(CONCURRENT)), return_exceptions=True
        )
        failures = [result for result in results if isinstance(result, BaseException)]
        assert not failures, [type(item).__name__ for item in failures]

        applied = [filename for result in results for filename in result]
        # Every script ran exactly once across all backends, and all of them ran.
        assert set(applied) == expected
        assert len(applied) == len(expected)

        async with engine.begin() as conn:
            rows = (await conn.execute(text("SELECT filename FROM schema_migrations"))).scalars()
            assert set(rows) == expected
            # The newest migration is there and usable, not half-created.
            count = (await conn.execute(text("SELECT count(*) FROM ai_usage"))).scalar_one()
            assert count == 0
    finally:
        await engine.dispose()
        admin = await asyncpg.connect(_asyncpg_dsn("postgres"))
        try:
            await admin.execute(f'DROP DATABASE IF EXISTS "{name}"')
        finally:
            await admin.close()
