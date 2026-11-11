"""Admin overrides win over `.env`, without a restart."""

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
    assert config.budget_usd == pytest.approx(target)
    assert config.max_items_per_run == 4


@pytest.mark.asyncio
async def test_clearing_returns_to_the_environment(clean_db) -> None:
    await overrides.save({"ai_monthly_budget_usd": 0.25}, updated_by="test@example.com")
    await overrides.clear(updated_by="test@example.com")
    config = await module.AIClient().config()
    assert config.budget_usd == get_settings().ai_monthly_budget_usd


@pytest.mark.asyncio
async def test_a_bad_stored_value_falls_back_to_env_instead_of_breaking(clean_db) -> None:
    await overrides.save({"ai_monthly_budget_usd": "not-a-number"}, updated_by="test@example.com")
    config = await module.AIClient().config()
    assert config.budget_usd == get_settings().ai_monthly_budget_usd


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
async def test_a_hand_edited_bad_calendar_falls_back_to_env(clean_db) -> None:
    # The API validates, but a direct database edit can still be wrong.
    await overrides.save({"ai_peak_windows": "01:00"}, updated_by="test@example.com")
    config = await module.AIClient().config()
    assert config.peak_windows == get_settings().ai_peak_windows
