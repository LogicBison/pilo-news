"""Admin overrides win over `.env`, without a restart."""

from datetime import UTC, datetime

import pytest

from news_api.articles.infrastructure import ai_client as module
from news_api.platform import overrides
from news_api.platform.settings import get_settings


@pytest.mark.asyncio
async def test_a_saved_override_replaces_the_environment_value(clean_db) -> None:
    default = get_settings().ai_monthly_budget_usd
    target = round(default / 4, 6)
    await overrides.save(
        {"ai_monthly_budget_usd": target, "ai_max_items_per_run": 4},
        updated_by="test@example.com",
    )
    config = await module.AIClient().config()
    assert config.limits.monthly_usd == pytest.approx(target)
    assert config.max_items_per_run == 4


@pytest.mark.asyncio
async def test_clearing_returns_to_the_environment(clean_db) -> None:
    await overrides.save({"ai_monthly_budget_usd": 0.25}, updated_by="test@example.com")
    await overrides.clear(updated_by="test@example.com")
    config = await module.AIClient().config()
    assert config.limits.monthly_usd == get_settings().ai_monthly_budget_usd


@pytest.mark.asyncio
async def test_a_bad_stored_value_falls_back_to_env_instead_of_breaking(clean_db) -> None:
    await overrides.save({"ai_monthly_budget_usd": "not-a-number"}, updated_by="test@example.com")
    config = await module.AIClient().config()
    assert config.limits.monthly_usd == get_settings().ai_monthly_budget_usd


@pytest.mark.asyncio
async def test_the_allowance_uses_the_overridden_ceiling(clean_db) -> None:
    await overrides.save(
        {"ai_monthly_budget_usd": 0.01, "ai_max_items_per_run": 50},
        updated_by="test@example.com",
    )
    ai = module.AIClient()
    allowance = await ai.allowance(interval_minutes=720, desks=11)
    # 1 cent over a month of runs cannot buy ten items.
    assert allowance < 10


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "moment",
    [
        datetime(2026, 11, 11, 12, 0, tzinfo=UTC),  # a weekday, off-peak hour
        datetime(2026, 11, 14, 12, 0, tzinfo=UTC),  # a Saturday: is_peak returns early
        datetime(2026, 11, 16, 2, 0, tzinfo=UTC),  # a weekday inside a peak block
    ],
)
async def test_a_hand_edited_bad_calendar_falls_back_to_env(
    clean_db, monkeypatch: pytest.MonkeyPatch, moment: datetime
) -> None:
    """The API validates, but a direct database edit can still be wrong.

    The fallback must not depend on the day the stack happens to boot: asking
    "is now peak?" skips the window parse entirely on a non-peak day.
    """
    monkeypatch.setattr(module, "utcnow", lambda: moment)
    await overrides.save({"ai_peak_windows": "01:00"}, updated_by="test@example.com")
    config = await module.AIClient().config()
    assert config.peak_windows == get_settings().ai_peak_windows


@pytest.mark.asyncio
async def test_every_cap_reaches_the_client_from_the_panel(clean_db) -> None:
    await overrides.save(
        {
            "ai_daily_token_limit": 5_000,
            "ai_monthly_token_limit": 90_000,
            "ai_daily_request_limit": 7,
            "ai_monthly_request_limit": 70,
            "ai_daily_budget_usd": 0.02,
            "ai_desks_per_tick": 3,
            "ai_rotation_minutes": 15,
        },
        updated_by="test@example.com",
    )
    config = await module.AIClient().config()
    assert config.limits.daily_tokens == 5_000
    assert config.limits.monthly_tokens == 90_000
    assert config.limits.daily_requests == 7
    assert config.limits.monthly_requests == 70
    assert config.limits.daily_usd == pytest.approx(0.02)
    assert config.limits.monthly_usd == get_settings().ai_monthly_budget_usd
    assert config.desks_per_tick == 3
    # The scheduler paces itself through the same row, without an AIConfig.
    assert await overrides.effective_int("ai_rotation_minutes", 60) == 15


@pytest.mark.asyncio
async def test_a_tiny_daily_token_cap_leaves_the_run_no_items(clean_db) -> None:
    """The day bucket binds even when the month still has plenty of room."""
    await overrides.save(
        {"ai_daily_token_limit": 600, "ai_monthly_token_limit": 10_000_000},
        updated_by="test@example.com",
    )
    ai = module.AIClient()
    assert await ai.allowance(interval_minutes=720, desks=1) == 0
