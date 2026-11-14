"""Desk rotation: which due channel starts now, and how often a rotation may start.

The spend ceiling lives in the ledger; this decides how the budget is spread.
A rotation that starved a channel would be a content bug, and one that ignored
its window would be a cost bug, so both are asserted here.
"""

from __future__ import annotations

import random
import time
from datetime import timedelta
from types import SimpleNamespace

import pytest

from news_api.articles.application import queue
from news_api.channels.domain.theme import Channel
from news_api.platform.clock import utcnow


def make_channel(slug: str, *, interval: int | None = None, auto: bool = True) -> Channel:
    return Channel(
        id=slug,
        slug=slug,
        code=slug.upper(),
        name=slug,
        base_name=slug,
        tagline="",
        theme={},
        locales=["en"],
        disclaimers={},
        cta={},
        timezone="UTC",
        retention_days=30,
        enabled=True,
        fetch_interval_minutes=interval,
        auto_fetch_enabled=auto,
    )


class _NoOverrides:
    async def effective_int(self, _key: str, default: int) -> int:
        return default


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def set(self, key: str, value: str, **_: object) -> None:
        self.store[key] = value


def due_pairs(slugs: list[str], *, weight: float = 1.0) -> list[tuple[Channel, float]]:
    return [(make_channel(slug), weight) for slug in slugs]


def test_every_due_desk_starts_when_there_is_room() -> None:
    due = due_pairs(["a", "b"])
    assert [channel.slug for channel in queue.select_desks(due, per_tick=5)] == ["a", "b"]


def test_a_rotation_starts_no_more_than_the_configured_desks() -> None:
    due = due_pairs(["a", "b", "c", "d", "e"])
    for seed in range(50):
        picked = queue.select_desks(due, per_tick=2, rng=random.Random(seed))
        assert len(picked) == 2
        assert len({channel.slug for channel in picked}) == 2
        assert all(channel.slug in "abcde" for channel in picked)


def test_a_zero_allowance_starts_nothing() -> None:
    assert queue.select_desks(due_pairs(["a", "b"]), per_tick=0) == []
    assert queue.select_desks([], per_tick=3) == []


def test_the_stalest_desk_wins_most_draws() -> None:
    stale = [(make_channel("stale"), 40.0)] + due_pairs(["b", "c", "d", "e"], weight=0.1)
    wins = sum(
        1
        for seed in range(300)
        if "stale"
        in [c.slug for c in queue.select_desks(stale, per_tick=1, rng=random.Random(seed))]
    )
    assert wins > 250


def test_a_heavy_desk_cannot_take_both_slots_forever() -> None:
    """Weighted sampling without replacement still lets the others through."""
    due = [(make_channel("heavy"), 100.0)] + due_pairs(["b", "c", "d"], weight=1.0)
    picked_second = {
        queue.select_desks(due, per_tick=2, rng=random.Random(seed))[1].slug for seed in range(200)
    }
    assert {"b", "c", "d"} <= picked_second


@pytest.mark.asyncio
async def test_a_rotation_window_holds_the_next_desks_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    channels = due_pairs(["a", "b", "c", "d"])
    fake = _FakeRedis()
    fake.store[queue.ROTATION_KEY] = str(time.time())
    started: list[str] = []

    async def fake_list_channels(*, enabled_only: bool = True) -> list[Channel]:
        return [channel for channel, _ in channels]

    async def fake_last_run(channel_id: str, *, trigger: str) -> dict[str, object]:
        return {"started_at": utcnow() - timedelta(hours=48)}

    async def fake_active_run(channel_id: str) -> None:
        return None

    async def fake_create_run(channel_id: str, *, trigger: str, requested_by: str) -> str:
        started.append(channel_id)
        return f"run-{channel_id}"

    async def fake_enqueue(**_: object) -> str:
        return "1-0"

    async def fake_get_redis() -> _FakeRedis:
        return fake

    monkeypatch.setattr(queue, "list_channels", fake_list_channels)
    monkeypatch.setattr(queue, "last_run", fake_last_run)
    monkeypatch.setattr(queue, "active_run", fake_active_run)
    monkeypatch.setattr(queue, "create_run", fake_create_run)
    monkeypatch.setattr(queue, "enqueue", fake_enqueue)
    monkeypatch.setattr(queue, "get_redis", fake_get_redis)
    monkeypatch.setattr(queue, "overrides", _NoOverrides())
    monkeypatch.setattr(
        queue,
        "get_settings",
        lambda: SimpleNamespace(
            refresh_interval_minutes=720, ai_desks_per_tick=2, ai_rotation_minutes=60
        ),
    )

    assert await queue.scheduler_tick() == 0
    assert started == []


@pytest.mark.asyncio
async def test_an_open_window_starts_the_subset_and_marks_the_rotation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    channels = due_pairs(["a", "b", "c", "d"])
    fake = _FakeRedis()
    started: list[str] = []

    async def fake_list_channels(*, enabled_only: bool = True) -> list[Channel]:
        return [channel for channel, _ in channels]

    async def fake_last_run(channel_id: str, *, trigger: str) -> dict[str, object]:
        return {"started_at": utcnow() - timedelta(hours=48)}

    async def fake_active_run(channel_id: str) -> None:
        return None

    async def fake_create_run(channel_id: str, *, trigger: str, requested_by: str) -> str:
        started.append(channel_id)
        return f"run-{channel_id}"

    async def fake_enqueue(**kwargs: object) -> str:
        assert kwargs["trigger"] == "schedule"
        return "1-0"

    async def fake_get_redis() -> _FakeRedis:
        return fake

    monkeypatch.setattr(queue, "list_channels", fake_list_channels)
    monkeypatch.setattr(queue, "last_run", fake_last_run)
    monkeypatch.setattr(queue, "active_run", fake_active_run)
    monkeypatch.setattr(queue, "create_run", fake_create_run)
    monkeypatch.setattr(queue, "enqueue", fake_enqueue)
    monkeypatch.setattr(queue, "get_redis", fake_get_redis)
    monkeypatch.setattr(queue, "overrides", _NoOverrides())
    monkeypatch.setattr(
        queue,
        "get_settings",
        lambda: SimpleNamespace(
            refresh_interval_minutes=720, ai_desks_per_tick=2, ai_rotation_minutes=60
        ),
    )

    assert await queue.scheduler_tick(rng=random.Random(7)) == 2
    assert len(set(started)) == 2
    assert queue.ROTATION_KEY in fake.store


@pytest.mark.asyncio
async def test_an_unreadable_rotation_marker_fails_open(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pacing is not a safety control: a Redis outage must not stop publishing."""

    async def broken() -> None:
        raise RuntimeError("redis down")

    monkeypatch.setattr(queue, "get_redis", broken)
    assert await queue._rotation_open(60) is True
