from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path

from sqlalchemy import text

from news_api.platform.db import engine
from news_api.platform.logging import configure_logging, get_logger
from news_api.platform.paths import app_root
from news_api.platform.settings import get_settings

log = get_logger(__name__)

MIGRATIONS_DIR = app_root() / "migrations"

LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename TEXT PRIMARY KEY,
    checksum TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def run_migrations(migrations_dir: Path | None = None) -> list[str]:
    """Apply numbered SQL scripts in order, exactly once, and return newly applied names."""
    directory = migrations_dir or MIGRATIONS_DIR
    files = sorted(directory.glob("*.sql"))
    if not files:
        log.warning("migrations.none_found", directory=str(directory))
        return []

    applied_now: list[str] = []
    async with engine.begin() as conn:
        await conn.execute(text(LEDGER_DDL))
        result = await conn.execute(text("SELECT filename, checksum FROM schema_migrations"))
        applied = {str(row[0]): str(row[1]) for row in result.all()}

        for path in files:
            digest = _checksum(path)
            previous = applied.get(path.name)
            if previous is not None:
                if previous != digest:
                    raise RuntimeError(
                        f"migration {path.name} changed after being applied; "
                        "add a new script instead"
                    )
                continue
            sql = path.read_text(encoding="utf-8")
            raw = await conn.get_raw_connection()
            if raw is None:
                raise RuntimeError("could not open a raw migration connection")
            driver = raw.driver_connection
            if driver is None:
                raise RuntimeError("could not open an asyncpg migration connection")
            await driver.execute(sql)
            await conn.execute(
                text("INSERT INTO schema_migrations (filename, checksum) VALUES (:name, :sum)"),
                {"name": path.name, "sum": digest},
            )
            applied_now.append(path.name)
            log.info("migrations.applied", filename=path.name)

    log.info("migrations.done", applied=len(applied_now), total=len(files), result="ok")
    return applied_now


async def migrations_applied() -> bool:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM schema_migrations"))
            count = int(result.scalar_one())
            expected = len(list(MIGRATIONS_DIR.glob("*.sql")))
            return count >= expected
    except Exception:
        return False


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    asyncio.run(run_migrations())


if __name__ == "__main__":
    main()
