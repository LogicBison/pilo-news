from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure.repo import record_audit
from news_api.offers.application.build import build_offer_issue
from news_api.offers.application.config import definition_for
from news_api.offers.domain.cadence import latest_due_date
from news_api.offers.infrastructure.repo import (
    get_issue,
    get_issue_by_id,
    issue_dto,
    list_issues,
    mark_issue,
    publish_issue,
    unpublish_issue,
    upsert_issue,
)
from news_api.platform.clock import utcnow
from news_api.platform.errors import Conflict, NotFound, ValidationProblem

router = APIRouter(prefix="/v1/admin/offers", tags=["admin"])


class OfferBuildRequest(BaseModel):
    industry: str = Field(min_length=2, max_length=40)
    offer: str | None = Field(default=None, max_length=120)
    issue_date: date | None = None
    dry_run: bool = False
    force: bool = False


class OfferPublishRequest(BaseModel):
    reviewer: str = Field(min_length=2, max_length=120)


@router.get("", dependencies=[Depends(admin_auth)])
async def list_offer_issues(
    industry: str | None = None, status: str | None = None, limit: int = 20
) -> Any:
    industry_id = None
    if industry:
        channel = await channels_repo.get_channel(industry, enabled_only=False)
        if not channel:
            raise NotFound(f"No industry with slug '{industry}'.")
        industry_id = channel.id
    rows = await list_issues(industry_id=industry_id, status=status, limit=limit)
    return {"data": [issue_dto(row) for row in rows]}


@router.get("/{issue_id}", dependencies=[Depends(admin_auth)])
async def get_offer_issue(issue_id: str) -> Any:
    try:
        UUID(issue_id)
    except ValueError:
        raise NotFound("Offer issue not found.") from None
    row = await get_issue_by_id(issue_id)
    if not row:
        raise NotFound("Offer issue not found.")
    return {"data": issue_dto(row)}


@router.post("/build", dependencies=[Depends(admin_mutation)])
async def trigger_offer_build(
    payload: OfferBuildRequest, request: Request, response: Response
) -> Any:
    definition = definition_for(payload.industry, payload.offer)
    if not definition:
        raise NotFound(f"No offer definition for '{payload.industry}'.")
    channel = await channels_repo.get_channel(payload.industry, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{payload.industry}'.")
    target = payload.issue_date or latest_due_date(definition.cadence, utcnow().date())
    if target is None:
        raise ValidationProblem("Invalid cadence for this offer.")

    if payload.dry_run:
        result = await build_offer_issue(
            payload.industry,
            offer_slug=definition.offer_slug,
            issue_date=target,
            dry_run=True,
        )
        return {"data": result}

    existing = await get_issue(
        industry_id=channel.id, offer_slug=definition.offer_slug, issue_date=target
    )
    if existing and existing["status"] in ("queued", "building") and not payload.force:
        raise Conflict("This offer issue is already being generated.")
    issue = await upsert_issue(
        industry_id=channel.id,
        offer_slug=definition.offer_slug,
        issue_date=target,
        scope=definition.scope,
        status="queued",
        title=definition.name,
        standfirst="",
    )
    if not issue:
        raise Conflict("Could not queue the offer issue.")
    from news_api.articles.application.queue import enqueue_offer

    try:
        await enqueue_offer(
            issue_id=str(issue["id"]),
            industry=payload.industry,
            offer=definition.offer_slug,
            issue_date=target.isoformat(),
        )
    except Exception as exc:
        await mark_issue(
            issue_id=str(issue["id"]),
            status="failed",
            error=f"enqueue_failed: {type(exc).__name__}",
        )
        raise
    await record_audit(
        actor=request.state.operator["email"],
        action="offer.build",
        entity="offer_issue",
        entity_id=str(issue["id"]),
        payload={"industry": payload.industry, "offer": definition.offer_slug},
    )
    response.status_code = 202
    return {
        "issue_id": str(issue["id"]),
        "industry": payload.industry,
        "offer": definition.offer_slug,
        "issue_date": target.isoformat(),
        "status": "queued",
    }


@router.post("/{issue_id}/publish", dependencies=[Depends(admin_mutation)])
async def publish_offer_issue(issue_id: str, payload: OfferPublishRequest, request: Request) -> Any:
    try:
        UUID(issue_id)
    except ValueError:
        raise NotFound("Offer issue not found.") from None
    reviewer = payload.reviewer.strip()
    if len(reviewer) < 2:
        raise ValidationProblem("A named reviewer is required to publish.")
    row = await publish_issue(issue_id, reviewer)
    if not row:
        raise Conflict("Only a draft with at least one row can be published.")
    await record_audit(
        actor=request.state.operator["email"],
        action="offer.publish",
        entity="offer_issue",
        entity_id=issue_id,
        payload={"reviewer": reviewer},
    )
    stored = await get_issue_by_id(issue_id)
    return {"data": issue_dto(stored) if stored else None}


@router.post("/{issue_id}/unpublish", dependencies=[Depends(admin_mutation)])
async def unpublish_offer_issue(issue_id: str, request: Request) -> Any:
    try:
        UUID(issue_id)
    except ValueError:
        raise NotFound("Offer issue not found.") from None
    row = await unpublish_issue(issue_id)
    if not row:
        raise Conflict("Only a published issue can be unpublished.")
    await record_audit(
        actor=request.state.operator["email"],
        action="offer.unpublish",
        entity="offer_issue",
        entity_id=issue_id,
    )
    stored = await get_issue_by_id(issue_id)
    return {"data": issue_dto(stored) if stored else None}
