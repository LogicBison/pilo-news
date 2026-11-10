"""Publisher-facing traffic pages, addressed by an unguessable token.

The page exists to answer one question in an acquisition conversation: what
did this desk send us? It exposes the source's own numbers only — no other
source, no reader data, no internal ids.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from news_api.platform.errors import NotFound
from news_api.sources.infrastructure import repo as sources_repo

router = APIRouter(prefix="/v1", tags=["traffic"])


@router.get("/traffic/{token}")
async def traffic(token: str) -> Any:
    summary = await sources_repo.traffic_summary(token)
    if not summary:
        raise NotFound("No traffic page for this token.")
    return {"data": summary}
