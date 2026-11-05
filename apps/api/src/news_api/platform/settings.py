from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings sourced from the root .env.<env> file via the container environment."""

    model_config = SettingsConfigDict(extra="ignore", case_sensitive=False)

    app_env: str = "dev"
    app_base_url: str = "http://localhost:3000"
    log_level: str = "info"

    database_url: str = "postgresql+asyncpg://news:news@postgres:5432/news"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "change-me"

    ai_base_url: str = "https://api.deepseek.com"
    ai_model: str = "deepseek-flash"
    ai_api_key: str = ""
    ai_monthly_budget_usd: float = 20.0
    ai_max_items_per_run: int = 60
    refresh_interval_minutes: int = 720

    metrics_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
