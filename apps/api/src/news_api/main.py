from fastapi import FastAPI

from news_api.platform.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="System News API",
    version="0.1.0",
    docs_url="/v1/docs",
    openapi_url="/v1/openapi.json",
)


@app.get("/v1/health", tags=["system"])
async def health() -> dict[str, str]:
    """Liveness probe. Dependency checks are added in M2."""
    return {"status": "ok", "service": "api", "env": settings.app_env}
