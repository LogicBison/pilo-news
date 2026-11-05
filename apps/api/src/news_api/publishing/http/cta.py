from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import public_access
from news_api.platform.errors import NotFound
from news_api.platform.metrics import CTA_EVENTS
from news_api.platform.security import hash_personal
from news_api.publishing.infrastructure import repo

router = APIRouter(prefix="/v1", tags=["leads"])


class CtaEventRequest(BaseModel):
    industry: str = Field(min_length=2, max_length=40)
    event: Literal["cta_impression", "cta_click", "lead_form_start", "lead_submit"]
    placement: str = Field(default="", max_length=40)
    locale: str = Field(default="en", max_length=10)
    article_id: str | None = Field(default=None, max_length=36)
    session_hash: str | None = Field(default=None, max_length=120)
    result: str | None = Field(default=None, max_length=40)


@router.post(
    "/cta-events",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(public_access)],
)
async def record_cta_event(payload: CtaEventRequest, request: Request) -> Response:
    channel = await channels_repo.get_channel(payload.industry, enabled_only=True)
    if not channel:
        raise NotFound("Unknown industry.")
    session_hash = hash_personal(payload.session_hash or "")[:32]
    await repo.insert_cta_event(
        industry_id=channel.id,
        event=payload.event,
        placement=payload.placement,
        locale=payload.locale,
        article_id=payload.article_id,
        session_hash=session_hash,
        result=payload.result,
    )
    CTA_EVENTS.labels(
        industry=channel.slug, event=payload.event, placement=payload.placement or "-"
    ).inc()
    return Response(status_code=204)
