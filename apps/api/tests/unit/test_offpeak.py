"""The provider's peak calendar: two weekday blocks, half price everywhere else."""

from datetime import UTC, datetime

import pytest

from news_api.platform.offpeak import (
    is_offpeak,
    is_peak,
    parse_hhmm,
    parse_peak_days,
    parse_peak_holidays,
    parse_peak_windows,
)

WINDOWS = "01:00-04:00,06:00-10:00"
DAYS = "1,2,3,4,5"


def _at(day: int, hour: int, minute: int = 0) -> datetime:
    # November 2026: the 10th is a Tuesday, the 14th a Saturday.
    return datetime(2026, 11, day, hour, minute, tzinfo=UTC)


def test_the_two_published_peak_blocks_are_peak() -> None:
    assert is_peak(_at(10, 1, 0), windows=WINDOWS, days=DAYS) is True
    assert is_peak(_at(10, 3, 59), windows=WINDOWS, days=DAYS) is True
    assert is_peak(_at(10, 6, 0), windows=WINDOWS, days=DAYS) is True
    assert is_peak(_at(10, 9, 59), windows=WINDOWS, days=DAYS) is True


def test_edges_are_half_open() -> None:
    assert is_peak(_at(10, 4, 0), windows=WINDOWS, days=DAYS) is False
    assert is_peak(_at(10, 10, 0), windows=WINDOWS, days=DAYS) is False


def test_the_afternoon_is_cheap() -> None:
    # The old 16:30-08:30 window blocked exactly these hours.
    assert is_peak(_at(10, 12, 0), windows=WINDOWS, days=DAYS) is False
    assert is_peak(_at(10, 16, 30), windows=WINDOWS, days=DAYS) is False
    assert is_peak(_at(10, 23, 0), windows=WINDOWS, days=DAYS) is False


def test_weekends_are_cheap_all_day() -> None:
    assert is_peak(_at(14, 2, 0), windows=WINDOWS, days=DAYS) is False
    assert is_peak(_at(15, 7, 0), windows=WINDOWS, days=DAYS) is False


def test_provider_holidays_are_cheap() -> None:
    holidays = "2026-11-10"
    assert is_offpeak(_at(10, 2, 0), windows=WINDOWS, days=DAYS, holidays=holidays) is True


def test_an_empty_calendar_has_no_peak() -> None:
    assert is_peak(_at(10, 2, 0), windows="", days="") is False


def test_a_window_may_cross_midnight() -> None:
    assert is_peak(_at(10, 23, 0), windows="22:00-02:00", days=DAYS) is True
    assert is_peak(_at(10, 1, 0), windows="22:00-02:00", days=DAYS) is True
    assert is_peak(_at(10, 12, 0), windows="22:00-02:00", days=DAYS) is False


def test_bad_values_are_rejected() -> None:
    with pytest.raises(ValueError):
        parse_hhmm("25:00")
    with pytest.raises(ValueError):
        parse_hhmm("8:30")
    with pytest.raises(ValueError):
        parse_peak_windows("01:00")
    with pytest.raises(ValueError):
        parse_peak_windows("01:00-01:00")
    with pytest.raises(ValueError):
        parse_peak_days("8")
    with pytest.raises(ValueError):
        parse_peak_holidays("2026-13-01")


@pytest.mark.asyncio
async def test_ai_client_refuses_peak_calls_when_offpeak_only(monkeypatch) -> None:
    from news_api.articles.infrastructure import ai_client as module
    from news_api.platform.settings import get_settings

    monkeypatch.setenv("AI_ENABLED", "true")
    monkeypatch.setenv("AI_API_KEY", "test-key")
    monkeypatch.setenv("AI_OFFPEAK_ONLY", "true")
    get_settings.cache_clear()
    try:
        monkeypatch.setattr(module, "utcnow", lambda: _at(10, 2, 0))  # Tuesday peak
        assert await module.AIClient().available() is False
        monkeypatch.setattr(module, "utcnow", lambda: _at(10, 12, 0))  # cheap afternoon
        assert await module.AIClient().available() is True
        monkeypatch.setenv("AI_OFFPEAK_ONLY", "false")
        get_settings.cache_clear()
        assert await module.AIClient().available() is True
    finally:
        get_settings.cache_clear()
