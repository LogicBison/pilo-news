from functools import lru_cache

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

    rate_limit_keyless: int = 120
    rate_limit_keyed: int = 600
    contact_rate_limit_per_hour: int = 3
    lead_rate_limit_per_hour: int = 5
    login_rate_limit_per_min: int = 5

    metrics_enabled: bool = True
    ssrf_allow_private: bool = False
    trust_forwarded_for: bool = True

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    contact_to: str = "news@example.com"
    next_public_api_base: str = "http://localhost:8080"
    sn_default_locale: str = "en"
    sn_default_industry: str = "legal"

    @property
    def cookie_secure(self) -> bool:
        return self.app_env == "prd"

    @property
    def supported_locales(self) -> tuple[str, ...]:
        return ("en", "es")


@lru_cache
def get_settings() -> Settings:
    return Settings()
