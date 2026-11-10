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
    ai_monthly_budget_usd: float = 20.0
    ai_max_items_per_run: int = 60
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
