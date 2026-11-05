from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache
def app_root() -> Path:
    """Locate config/ and migrations/ in both editable (dev) and wheel (prd) installs."""
    configured = os.environ.get("APP_ROOT")
    if configured:
        return Path(configured)
    for parent in Path(__file__).resolve().parents:
        if (parent / "migrations").is_dir() and (parent / "config").is_dir():
            return parent
    current = Path.cwd()
    if (current / "migrations").is_dir() or (current / "config").is_dir():
        return current
    return Path("/app")
