from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure import ops_repo
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform.errors import Conflict, NotFound, ValidationProblem

router = APIRouter(prefix="/v1/admin", tags=["admin"])


class HideRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=200)


class PinCreate(BaseModel):
    article_id: str
    position: int = Field(ge=1, le=5)
    weight: float = Field(default=1.0, gt=0, le=10)
    expires_hours: int = Field(default=72, ge=1, le=720)


def article_dto(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "url": row["canonical_url"],
        "publisher": row["publisher"],
        "language": row["language"],
        "published_at": row["published_at"],
        "industry": row["industry_slug"],
        "status": row["status"],
        "hidden_reason": row.get("hidden_reason"),
        "summary": row.get("summary"),
        "excerpt": row.get("excerpt"),
        "score": float(row.get("score") or 0),
        "corroboration": int(row.get("corroboration") or 1),
        "verification": row.get("verification"),
        "is_seed": bool(row.get("is_seed")),
    }


def pin_dto(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "article_id": str(row["article_id"]),
        "position": int(row["position"]),
        "weight": float(row["weight"]),
        "expires_at": row["pin_expires_at"],
        "created_at": row["created_at"],
        "title": row.get("title"),
        "language": row.get("language"),
        "status": row.get("status"),
    }


@router.get("/articles", dependencies=[Depends(admin_auth)])
async def list_articles(industry: str | None = None, status: str | None = None) -> Any:
    industry_id = None
    if industry:
        channel = await channels_repo.get_channel(industry, enabled_only=False)
        if not channel:
            raise NotFound(f"No industry with slug '{industry}'.")
        industry_id = channel.id
    rows = await ops_repo.admin_articles(industry_id=industry_id, status=status)
    return {"data": [article_dto(row) for row in rows]}


@router.post("/articles/{article_id}/hide", dependencies=[Depends(admin_mutation)])
async def hide_article(article_id: str, payload: HideRequest, request: Request) -> Any:
    article = await ops_repo.get_article_admin(article_id)
    if not article:
        raise NotFound("Article not found.")
    await ops_repo.set_article_status(article_id, "hidden", payload.reason)
    await record_audit(
        actor=request.state.operator["email"],
        action="article.hide",
        entity="article",
        entity_id=article_id,
        payload={"reason": payload.reason, "before": article["status"]},
    )
    return {"data": {"id": article_id, "status": "hidden"}}


@router.post("/articles/{article_id}/unhide", dependencies=[Depends(admin_mutation)])
async def unhide_article(article_id: str, request: Request) -> Any:
    article = await ops_repo.get_article_admin(article_id)
    if not article:
        raise NotFound("Article not found.")
    await ops_repo.set_article_status(article_id, "published", None)
    await record_audit(
        actor=request.state.operator["email"],
        action="article.unhide",
        entity="article",
        entity_id=article_id,
        payload={"before": article["status"]},
    )
    return {"data": {"id": article_id, "status": "published"}}


@router.get("/pins", dependencies=[Depends(admin_auth)])
async def list_pins(industry: str) -> Any:
    channel = await channels_repo.get_channel(industry, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{industry}'.")
    rows = await ops_repo.list_pins(channel.id)
    return {"data": [pin_dto(row) for row in rows]}


@router.post("/pins", status_code=201, dependencies=[Depends(admin_mutation)])
async def create_pin(payload: PinCreate, request: Request) -> Any:
    article = await ops_repo.get_article_admin(payload.article_id)
    if not article:
        raise NotFound("Article not found.")
    if article["status"] != "published":
        raise ValidationProblem("Only published articles can be pinned.")
    channel = await channels_repo.get_channel(article["industry_slug"], enabled_only=False)
    if not channel:
        raise NotFound("Article channel not found.")
    row = await ops_repo.create_pin(
        article_id=payload.article_id,
        industry_id=channel.id,
        position=payload.position,
        weight=payload.weight,
        expires_hours=payload.expires_hours,
    )
    if not row:
        raise Conflict("That pin position is already occupied for this channel.")
    await record_audit(
        actor=request.state.operator["email"],
        action="pin.create",
        entity="pin",
        entity_id=str(row["id"]),
        payload={
            "article_id": payload.article_id,
            "industry": channel.slug,
            "position": payload.position,
        },
    )
    return {
        "data": pin_dto(
            {
                **row,
                "title": article["title"],
                "language": article["language"],
                "status": article["status"],
            }
        )
    }


@router.delete(
    "/pins/{pin_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(admin_mutation)],
)
async def delete_pin(pin_id: str, request: Request) -> None:
    if not await ops_repo.delete_pin(pin_id):
        raise NotFound("Pin not found.")
    await record_audit(
        actor=request.state.operator["email"],
        action="pin.delete",
        entity="pin",
        entity_id=pin_id,
    )
