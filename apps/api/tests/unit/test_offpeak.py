"""DeepSeek calls are limited to the provider's off-peak UTC window."""

from datetime import UTC, datetime

import pytest

from news_api.platform.offpeak import in_window, parse_hhmm


def _at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, 10, hour, minute, tzinfo=UTC)


def test_window_wraps_midnight() -> None:
    assert in_window(_at(18, 0), "16:30", "08:30") is True
    assert in_window(_at(23, 59), "16:30", "08:30") is True
    assert in_window(_at(0, 30), "16:30", "08:30") is True
    assert in_window(_at(8, 29), "16:30", "08:30") is True


def test_peak_hours_are_outside() -> None:
    assert in_window(_at(8, 30), "16:30", "08:30") is False
    assert in_window(_at(12, 0), "16:30", "08:30") is False
    assert in_window(_at(16, 29), "16:30", "08:30") is False


def test_a_same_day_window_still_works() -> None:
    assert in_window(_at(10, 0), "09:00", "17:00") is True
    assert in_window(_at(18, 0), "09:00", "17:00") is False


def test_empty_window_spends_nothing() -> None:
    assert in_window(_at(12, 0), "10:00", "10:00") is False


def test_bad_values_are_rejected() -> None:
    with pytest.raises(ValueError):
        parse_hhmm("25:00")
    with pytest.raises(ValueError):
        parse_hhmm("8:30")


def test_ai_client_refuses_peak_calls_when_offpeak_only(monkeypatch) -> None:
    from news_api.articles.infrastructure import ai_client as module
    from news_api.platform.settings import get_settings

    monkeypatch.setenv("AI_ENABLED", "true")
    monkeypatch.setenv("AI_API_KEY", "test-key")
    monkeypatch.setenv("AI_OFFPEAK_ONLY", "true")
    get_settings.cache_clear()
    try:
        monkeypatch.setattr(module, "utcnow", lambda: _at(12, 0))
        assert module.AIClient().available() is False
        monkeypatch.setattr(module, "utcnow", lambda: _at(18, 0))
        assert module.AIClient().available() is True
        monkeypatch.setenv("AI_OFFPEAK_ONLY", "false")
        get_settings.cache_clear()
        assert module.AIClient().available() is True
    finally:
        get_settings.cache_clear()
