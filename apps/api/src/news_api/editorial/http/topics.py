from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure import ops_repo
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform.errors import Conflict, NotFound
from news_api.platform.jsons import as_dict

router = APIRouter(prefix="/v1/admin/topics", tags=["admin"])


class TopicCreate(BaseModel):
    industry: str = Field(min_length=2, max_length=40)
    slug: str = Field(pattern="^[a-z0-9-]{2,40}$")
    label: dict[str, str] = Field(default_factory=lambda: {"en": "", "es": ""})
    weight: float = Field(default=1.0, gt=0, le=10)
    keywords: dict[str, list[str]] = Field(default_factory=dict)


class TopicUpdate(BaseModel):
    slug: str | None = Field(default=None, pattern="^[a-z0-9-]{2,40}$")
    label: dict[str, str] | None = None
    weight: float | None = Field(default=None, gt=0, le=10)
    keywords: dict[str, list[str]] | None = None


def topic_dto(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "industry_id": str(row["industry_id"]),
        "slug": row["slug"],
        "label": as_dict(row.get("label")),
        "weight": float(row["weight"]),
        "keywords": as_dict(row.get("keywords")),
    }


@router.get("", dependencies=[Depends(admin_auth)])
async def list_topics(industry: str) -> Any:
    channel = await channels_repo.get_channel(industry, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{industry}'.")
    rows = await ops_repo.list_topics_admin(channel.id)
    return {"data": [topic_dto(row) for row in rows]}


@router.post("", status_code=201, dependencies=[Depends(admin_mutation)])
async def create_topic(payload: TopicCreate, request: Request) -> Any:
    channel = await channels_repo.get_channel(payload.industry, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{payload.industry}'.")
    row = await ops_repo.create_topic(
        industry_id=channel.id,
        slug=payload.slug,
        label=payload.label,
        weight=payload.weight,
        keywords=payload.keywords,
    )
    if not row:
        raise Conflict("A topic with this slug already exists for this channel.")
    await record_audit(
        actor=request.state.operator["email"],
        action="topic.create",
        entity="topic",
        entity_id=str(row["id"]),
        payload={"industry": channel.slug, "slug": payload.slug},
    )
    return {"data": topic_dto(row)}


@router.patch("/{topic_id}", dependencies=[Depends(admin_mutation)])
async def update_topic(topic_id: str, payload: TopicUpdate, request: Request) -> Any:
    fields = payload.model_dump(exclude_unset=True)
    row = await ops_repo.update_topic(topic_id, fields)
    if not row:
        raise NotFound("Topic not found or no changes supplied.")
    await record_audit(
        actor=request.state.operator["email"],
        action="topic.update",
        entity="topic",
        entity_id=topic_id,
        payload={"fields": sorted(fields.keys())},
    )
    return {"data": topic_dto(row)}


@router.delete(
    "/{topic_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(admin_mutation)],
)
async def delete_topic(topic_id: str, request: Request) -> None:
    if not await ops_repo.delete_topic(topic_id):
        raise NotFound("Topic not found.")
    await record_audit(
        actor=request.state.operator["email"],
        action="topic.delete",
        entity="topic",
        entity_id=topic_id,
    )
