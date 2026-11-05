from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from news_api.platform.paths import app_root

CONFIG_DIR = app_root() / "config"


@lru_cache
def load_json(relative_path: str) -> dict[str, Any]:
    path = CONFIG_DIR / relative_path
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def scoring_config() -> dict[str, Any]:
    return load_json("scoring.json")


def seed_config() -> dict[str, Any]:
    return load_json("seeds.json")


def prompt_table(language: str) -> dict[str, Any]:
    return load_json(f"prompts/{language}.json")


def scoring_value(path: str, default: Any = None) -> Any:
    node: Any = scoring_config()
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node
