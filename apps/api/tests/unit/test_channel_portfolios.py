"""Every channel profile must stand on its own feed portfolio.

An article URL is globally unique in the database (`articles.canonical_url`), and
the upsert keeps the first channel that claimed it. Two channels sharing a feed
therefore do not duplicate a story: the second desk silently loses it. These
tests keep the portfolios disjoint and above the coverage floor so that bug
cannot come back through a profile edit.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

DEPLOYMENTS = Path(__file__).resolve().parents[2] / "config" / "deployments"
SUPPORTED_LOCALES = {"en", "es"}
MIN_SOURCES = 4


def _profiles() -> dict[str, list[dict]]:
    """slug -> sources, across every deployment profile in the repo."""
    channels: dict[str, list[dict]] = {}
    for path in sorted(DEPLOYMENTS.glob("*.json")):
        profile = json.loads(path.read_text())
        for industry in profile["industries"]:
            channels[industry["slug"]] = industry.get("sources", [])
    return channels


def _normalize(feed_url: str) -> str:
    parts = urlsplit(feed_url.strip())
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return f"{host}{parts.path.rstrip('/') or '/'}"


def test_no_feed_is_configured_for_two_channels() -> None:
    claimed: dict[str, list[str]] = defaultdict(list)
    for slug, sources in _profiles().items():
        for source in sources:
            claimed[_normalize(source["feed_url"])].append(slug)

    shared = {feed: slugs for feed, slugs in claimed.items() if len(set(slugs)) > 1}
    assert not shared, f"feeds shared across channels: {shared}"


def test_every_channel_meets_the_coverage_floor() -> None:
    for slug, sources in _profiles().items():
        enabled = [source for source in sources if source.get("enabled", True)]
        assert len(enabled) >= MIN_SOURCES, f"{slug} has {len(enabled)} sources"
        languages = {source["language"] for source in enabled}
        assert languages <= SUPPORTED_LOCALES, f"{slug} has an unsupported language"
        assert {"en", "es"} <= languages, f"{slug} is missing a language bundle"


def test_health_medicine_does_not_reuse_a_stem_cell_feed() -> None:
    """The rule the operator asked for: a stem-cell story stays on stem-cell."""
    channels = _profiles()
    stem_cell = {_normalize(source["feed_url"]) for source in channels["stem-cell"]}
    health = {_normalize(source["feed_url"]) for source in channels["health-medicine"]}
    assert not (stem_cell & health)
