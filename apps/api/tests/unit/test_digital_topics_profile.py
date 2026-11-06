"""The digital-technology demand test (M10) depends on these three topics."""

from __future__ import annotations

import json
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[2] / "config" / "deployments" / "cybersecurity.json"
REQUIRED = {"ai-infrastructure", "chips-supply", "ai-rules"}


def _topics() -> dict[str, dict]:
    profile = json.loads(PROFILE.read_text())
    channel = next(i for i in profile["industries"] if i["slug"] == "cybersecurity")
    return {topic["slug"]: topic for topic in channel["topics"]}


def test_profile_carries_the_demand_test_topics() -> None:
    assert set(_topics()) >= REQUIRED


def test_each_topic_is_bilingual_and_weighted() -> None:
    for slug in REQUIRED:
        topic = _topics()[slug]
        assert topic["label"]["en"] and topic["label"]["es"], slug
        assert 0 < topic["weight"] <= 10, slug
        assert topic["keywords"]["en"], slug
        assert topic["keywords"]["es"], slug
