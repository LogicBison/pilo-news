from __future__ import annotations

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


def test_channel_interval_wins_over_the_default() -> None:
    assert make_channel("a", interval=60).effective_fetch_interval(720) == 60
    assert make_channel("b").effective_fetch_interval(720) == 720


@pytest.mark.asyncio
async def test_scheduler_uses_the_channel_override_and_skips_paused_channels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    channels = [
        make_channel("fast", interval=60),
        make_channel("slow"),
        make_channel("paused", interval=15, auto=False),
    ]
    last_runs = {
        "fast": {"started_at": utcnow() - timedelta(minutes=120)},
        "slow": {"started_at": utcnow() - timedelta(minutes=120)},
        "paused": None,
    }
    created: list[str] = []
    enqueued: list[str] = []

    async def fake_list_channels(*, enabled_only: bool = True) -> list[Channel]:
        assert enabled_only is True
        return channels

    async def fake_last_run(channel_id: str, *, trigger: str) -> dict[str, object] | None:
        assert trigger == "schedule"
        return last_runs[channel_id]

    async def fake_active_run(channel_id: str) -> None:
        return None

    async def fake_create_run(channel_id: str, *, trigger: str, requested_by: str) -> str:
        assert trigger == "schedule"
        assert requested_by == "scheduler"
        created.append(channel_id)
        return f"run-{channel_id}"

    async def fake_enqueue(*, run_id: str, industry: str, trigger: str) -> str:
        assert trigger == "schedule"
        assert run_id == f"run-{industry}"
        enqueued.append(industry)
        return run_id

    monkeypatch.setattr(queue, "list_channels", fake_list_channels)
    monkeypatch.setattr(queue, "last_run", fake_last_run)
    monkeypatch.setattr(queue, "active_run", fake_active_run)
    monkeypatch.setattr(queue, "create_run", fake_create_run)
    monkeypatch.setattr(queue, "enqueue", fake_enqueue)
    monkeypatch.setattr(
        queue,
        "get_settings",
        lambda: SimpleNamespace(refresh_interval_minutes=720),
    )

    count = await queue.scheduler_tick()

    assert count == 1
    assert created == ["fast"]
    assert enqueued == ["fast"]


@pytest.mark.asyncio
async def test_scheduler_respects_the_override_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    channel = make_channel("fast", interval=60)

    async def fake_list_channels(*, enabled_only: bool = True) -> list[Channel]:
        return [channel]

    async def fake_last_run(channel_id: str, *, trigger: str) -> dict[str, object] | None:
        return {"started_at": utcnow() - timedelta(minutes=30)}

    async def fake_active_run(channel_id: str) -> None:
        return None

    created: list[str] = []

    async def fake_create_run(channel_id: str, *, trigger: str, requested_by: str) -> str:
        created.append(channel_id)
        return "run"

    async def fake_enqueue(**_: object) -> str:
        return "1-0"

    monkeypatch.setattr(queue, "list_channels", fake_list_channels)
    monkeypatch.setattr(queue, "last_run", fake_last_run)
    monkeypatch.setattr(queue, "active_run", fake_active_run)
    monkeypatch.setattr(queue, "create_run", fake_create_run)
    monkeypatch.setattr(queue, "enqueue", fake_enqueue)
    monkeypatch.setattr(
        queue,
        "get_settings",
        lambda: SimpleNamespace(refresh_interval_minutes=720),
    )

    count = await queue.scheduler_tick()

    assert count == 0
    assert created == []
