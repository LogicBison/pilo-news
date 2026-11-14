from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings sourced from the root .env.<env> file via the container environment."""

    model_config = SettingsConfigDict(extra="ignore", case_sensitive=False)

    app_env: str = "dev"
    app_domain: str = "localhost"
    app_base_url: str = "http://localhost:3000"
    api_port: int = 8080
    web_port: int = 3000
    log_level: str = "info"
    log_json: bool = True
    # A request slower than this is a main event and gets logged at info even
    # when successful. Everything else successful stays at debug.
    log_slow_request_ms: int = 1000

    database_url: str = "postgresql+asyncpg://news:news@postgres:5432/news"
    redis_url: str = "redis://redis:6379/0"
    run_migrations: bool = True

    secret_key: str = "change-me"
    admin_email: str = "admin@example.com"
    admin_password: str = ""
    admin_password_hash: str = ""
    admin_session_minutes: int = 15

    ai_base_url: str = "https://api.deepseek.com"
    ai_model: str = "deepseek-flash"
    ai_api_key: str = ""
    ai_enabled: bool = True
    # The ceilings for every provider call this stack makes (item summaries,
    # desk briefs, picks, offer drafts). Three dimensions, because USD is
    # derived from a price table this stack does not control: tokens and
    # requests are what the provider bills and what its console shows. A call
    # must fit the day and the month on all three, so the first cap to bind
    # stops the spend.
    ai_daily_token_limit: int = 300_000
    ai_monthly_token_limit: int = 6_000_000
    ai_daily_request_limit: int = 400
    ai_monthly_request_limit: int = 12_000
    ai_daily_budget_usd: float = 0.25
    ai_monthly_budget_usd: float = 3.0
    ai_max_items_per_run: int = 60
    # Desk rotation and the failure breaker: how many channels one rotation may
    # start, how far apart rotations are, and how many consecutive provider
    # failures stop the stack until the cooldown expires.
    ai_desks_per_tick: int = 2
    ai_rotation_minutes: int = 60
    ai_breaker_failures: int = 5
    ai_breaker_seconds: int = 1800
    # DeepSeek peak is Mon-Fri, 01:00-04:00 and 06:00-10:00 UTC; every other
    # hour is half price. With this on, no provider call is made inside a peak
    # window: the run publishes without summaries and the next cheap run
    # backfills them.
    ai_offpeak_only: bool = False
    ai_peak_windows: str = "01:00-04:00,06:00-10:00"
    # ISO weekday numbers, Monday = 1.
    ai_peak_days: str = "1,2,3,4,5"
    # Provider holidays (YYYY-MM-DD, comma separated) are off-peak all day.
    ai_peak_holidays: str = ""
    # Log once when this share of the ceiling has been spent.
    ai_budget_alert_ratio: float = 0.8
    # Planning number used only to size a run's item allowance, not accounting.
    ai_item_cost_estimate_usd: float = 0.00016
    ai_item_timeout_seconds: float = 120.0
    ai_desk_timeout_seconds: float = 45.0
    ai_picks_timeout_seconds: float = 60.0
    refresh_interval_minutes: int = 720

    # --- crawler identity and pacing (fetch-safety SPEC, R1-R5) ------------
    # One identity, used by both fetchers (articles and offers). The contact
    # URL must be a page a publisher can actually reach.
    bot_name: str = "HeraldFoxBot"
    bot_version: str = "1.0"
    bot_url: str = "https://heraldfox.com/bot"
    # enforce = delay for real; shadow = compute and log the delay without
    # applying it; off = no floor, cap or breaker (429 cooldowns still apply -
    # the server asked for them explicitly).
    fetch_pacing: Literal["off", "shadow", "enforce"] = "enforce"
    fetch_host_floor_s: float = 5.0
    fetch_host_hourly_cap: int = 20
    fetch_robots_ttl_s: int = 24 * 60 * 60
    fetch_breaker_failures: int = 5
    fetch_breaker_seconds: int = 30 * 60
    fetch_retry_base_s: float = 60.0
    fetch_cooldown_cap_s: int = 6 * 60 * 60
    fetch_challenge_cooldown_s: int = 60 * 60
    # A publisher that says no stays refused for a week: long enough not to
    # pester, short enough that a licence or a robots change is picked up.
    fetch_denied_cooldown_s: int = 7 * 24 * 60 * 60

    @field_validator("ai_peak_windows")
    @classmethod
    def _peak_windows_are_hhmm(cls, value: str) -> str:
        from news_api.platform.offpeak import parse_peak_windows

        parse_peak_windows(value)
        return value

    @field_validator("ai_peak_days")
    @classmethod
    def _peak_days_are_weekdays(cls, value: str) -> str:
        from news_api.platform.offpeak import parse_peak_days

        parse_peak_days(value)
        return value

    @field_validator("*", mode="before")
    @classmethod
    def _empty_non_string_uses_default(cls, value, info):
        """Blank env line means "unset" for every non-string setting.

        The canonical env layout writes ``KEY=`` for a key an operator has not
        filled in yet. Empty is a valid string, but it is not a valid int,
        float, bool or literal: ``LOG_SLOW_REQUEST_MS=`` stopped the production
        API from importing. String fields keep their empty value, because some
        of them (``SMTP_TRANSPORT``) use empty as a real setting.
        """
        if isinstance(value, str) and not value.strip():
            field = cls.model_fields.get(info.field_name)
            if field is not None and field.annotation is not str:
                return field.default
        return value

    @field_validator(
        "bot_name",
        "bot_version",
        "bot_url",
        "fetch_pacing",
        "fetch_host_floor_s",
        "fetch_host_hourly_cap",
        "fetch_robots_ttl_s",
        "fetch_breaker_failures",
        "fetch_breaker_seconds",
        "fetch_retry_base_s",
        "fetch_cooldown_cap_s",
        "fetch_challenge_cooldown_s",
        "fetch_denied_cooldown_s",
        "ai_peak_windows",
        "ai_peak_days",
        "ai_peak_holidays",
        mode="before",
    )
    @classmethod
    def _empty_crawler_value_uses_default(cls, value, info):
        """Treat an empty crawler key as unset.

        The canonical env layout gives every reference key a line in every
        file, materialised as ``KEY=`` until an operator fills it (env-sync).
        An empty string would otherwise override the default and, for
        ``FETCH_PACING``, fail validation at startup. Blank means "unset" for
        these keys only; other empty values keep their existing meaning.
        """
        if isinstance(value, str) and not value.strip():
            return cls.model_fields[info.field_name].default
        return value

    rate_limit_keyless: int = 120
    rate_limit_keyed: int = 600
    contact_rate_limit_per_hour: int = 3
    lead_rate_limit_per_hour: int = 5
    login_rate_limit_per_min: int = 5

    metrics_enabled: bool = True
    ssrf_allow_private: bool = False
    trust_forwarded_for: bool = True
    # Empty disables country capture. Set to the edge header that overwrites it,
    # for example "cf-ipcountry". Never trust a client-supplied value.
    geo_country_header: str = ""

    # --- email transport (contact/lead notifications) ----------------------
    # SMTP_TRANSPORT selects where a message is handed off; the sender is the
    # same on every lane:
    #   ""        the flat SMTP_* block (historical behaviour, any provider)
    #   gateway   the pilo-mail relay gateway -> Brevo from one fixed IP
    #   direct    pilo-mail submission (Mailu), delivered from the host itself
    # A selected lane with no host is not an error: the deployment simply does
    # not send, and every caller logs notify.skipped.
    smtp_transport: Literal["", "gateway", "direct"] = ""
    smtp_from: str = ""
    smtp_starttls: bool = True
    smtp_ssl: bool = False
    smtp_timeout_seconds: float = 10.0

    # Flat lane (only read when SMTP_TRANSPORT is empty).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # gateway lane: STARTTLS on 2525, one SASL account per integration.
    smtp_gateway_host: str = ""
    smtp_gateway_port: int = 2525
    smtp_gateway_user: str = ""
    smtp_gateway_password: str = ""
    smtp_gateway_ssl: bool = False

    # direct lane: pilo-mail submission; 465 is implicit TLS.
    smtp_direct_host: str = ""
    smtp_direct_port: int = 465
    smtp_direct_user: str = ""
    smtp_direct_password: str = ""
    smtp_direct_ssl: bool = True

    contact_to: str = "news@example.com"
    next_public_api_base: str = "http://localhost:8080"
    sn_default_locale: str = "en"
    sn_default_industry: str = "legal"

    @field_validator("smtp_transport", mode="before")
    @classmethod
    def _normalise_transport(cls, value: object) -> object:
        """Accept ``GATEWAY`` / `` Gateway ``; a real typo still fails the Literal."""
        return value.strip().lower() if isinstance(value, str) else value

    @property
    def cookie_secure(self) -> bool:
        return self.app_env == "prd"

    @property
    def supported_locales(self) -> tuple[str, ...]:
        return ("en", "es")


@lru_cache
def get_settings() -> Settings:
    return Settings()
