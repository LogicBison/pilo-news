"""Crawler settings must survive the canonical env layout.

env-sync gives every key a line in every env file, materialised as ``KEY=``
until an operator fills it. For the crawler keys a blank value has to mean
"unset": an empty string would either override the default or - for
``FETCH_PACING`` - fail validation and stop the API and the worker from
booting.
"""

from news_api.platform.settings import Settings


def test_blank_crawler_keys_fall_back_to_defaults() -> None:
    settings = Settings(
        bot_name="",
        bot_version=" ",
        bot_url="",
        fetch_pacing="",
        fetch_host_floor_s="",
        fetch_host_hourly_cap="",
    )
    assert settings.bot_name == "HeraldFoxBot"
    assert settings.bot_version == "1.0"
    assert settings.bot_url == "https://heraldfox.com/bot"
    assert settings.fetch_pacing == "enforce"
    assert settings.fetch_host_floor_s == 5.0
    assert settings.fetch_host_hourly_cap == 20


def test_blank_non_string_env_does_not_break_startup(monkeypatch) -> None:
    # The production failure: env-sync writes `LOG_SLOW_REQUEST_MS=` and the
    # API cannot import. Every non-string blank must fall back to its default.
    monkeypatch.setenv("LOG_SLOW_REQUEST_MS", "")
    monkeypatch.setenv("METRICS_ENABLED", "")
    monkeypatch.setenv("SMTP_TIMEOUT_SECONDS", "")
    settings = Settings()
    assert settings.log_slow_request_ms == 1000
    assert settings.metrics_enabled is True
    assert settings.smtp_timeout_seconds == 10


def test_blank_string_setting_keeps_its_empty_meaning(monkeypatch) -> None:
    # SMTP_TRANSPORT="" selects the flat SMTP lane; it must not become "gateway".
    monkeypatch.setenv("SMTP_TRANSPORT", "")
    assert Settings().smtp_transport == ""


def test_explicit_crawler_values_still_win() -> None:
    settings = Settings(fetch_pacing="shadow", bot_name="OtherBot", fetch_host_floor_s="2.5")
    assert settings.fetch_pacing == "shadow"
    assert settings.bot_name == "OtherBot"
    assert settings.fetch_host_floor_s == 2.5
