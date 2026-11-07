from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import public_access
from news_api.platform.errors import NotFound, ValidationProblem
from news_api.platform.metrics import CTA_EVENTS
from news_api.platform.security import hash_personal
from news_api.publishing.infrastructure import repo

router = APIRouter(prefix="/v1", tags=["leads"])


class CtaEventRequest(BaseModel):
    # Null on the apex lobby: that event belongs to no single desk.
    industry: str | None = Field(default=None, min_length=2, max_length=40)
    # Where a cross-desk event happened, e.g. "lobby".
    surface: str = Field(default="", max_length=40)
    event: Literal[
        "cta_impression",
        "cta_click",
        "lead_form_start",
        "lead_submit",
        "question_submit",
        "asset_interest",
        "brief_confirm",
        "desk_enter",
    ]
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
    channel = None
    if payload.industry:
        channel = await channels_repo.get_channel(payload.industry, enabled_only=True)
        if not channel:
            raise NotFound("Unknown industry.")
    elif not payload.surface:
        # Either a desk or a surface has to own the event, otherwise the funnel
        # gets rows nobody can attribute.
        raise ValidationProblem("Send either `industry` or `surface`.")

    session_hash = hash_personal(payload.session_hash or "")[:32]
    await repo.insert_cta_event(
        industry_id=channel.id if channel else None,
        event=payload.event,
        placement=payload.placement,
        locale=payload.locale,
        article_id=payload.article_id,
        session_hash=session_hash,
        result=payload.result,
        surface=payload.surface,
    )
    CTA_EVENTS.labels(
        industry=channel.slug if channel else (payload.surface or "-"),
        event=payload.event,
        placement=payload.placement or "-",
    ).inc()
    return Response(status_code=204)
