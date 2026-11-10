from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field

from news_api.articles.application.queue import enqueue
from news_api.articles.infrastructure.fetcher import fetch_source
from news_api.articles.infrastructure.politeness import HostLedger
from news_api.articles.infrastructure.repo import create_run
from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform.errors import Conflict, InvalidLocale, NotFound, ValidationProblem
from news_api.platform.i18n import normalize_locale
from news_api.sources.domain.validation import normalize_feed_url, validate_feed_url
from news_api.sources.infrastructure import repo as sources_repo
from news_api.sources.infrastructure.repo import source_dto

router = APIRouter(prefix="/v1/admin/sources", tags=["admin"])


class SourceCreate(BaseModel):
    industry: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    feed_url: str = Field(min_length=8, max_length=2048)
    language: str = Field(default="en", max_length=10)
    trust: float = Field(default=0.7, ge=0, le=1)
    enabled: bool = True
    allow_http: bool = False
    poll_interval_min: int = Field(default=720, ge=5, le=1440)
    terms_checked_at: datetime | None = None
    terms_url: str | None = Field(default=None, max_length=2048)


class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    feed_url: str | None = Field(default=None, min_length=8, max_length=2048)
    language: str | None = Field(default=None, max_length=10)
    trust: float | None = Field(default=None, ge=0, le=1)
    enabled: bool | None = None
    allow_http: bool | None = None
    poll_interval_min: int | None = Field(default=None, ge=5, le=1440)
    terms_checked_at: datetime | None = None
    terms_url: str | None = Field(default=None, max_length=2048)
    status: str | None = Field(default=None, pattern="^(active|blocked)$")


def validate_language(value: str) -> str:
    try:
        return normalize_locale(value)
    except InvalidLocale as exc:
        raise ValidationProblem("language must be a supported locale (en, es).") from exc


def validate_url(value: str, allow_http: bool) -> str:
    normalized = normalize_feed_url(value)
    problems = validate_feed_url(normalized, allow_http=allow_http)
    if problems:
        raise ValidationProblem("; ".join(problems))
    return normalized


async def channel_for_slug(slug: str) -> Any:
    channel = await channels_repo.get_channel(slug, enabled_only=False)
    if not channel:
        raise NotFound(f"No industry with slug '{slug}'.")
    return channel


@router.get("", dependencies=[Depends(admin_auth)])
async def list_sources(industry: str | None = None) -> Any:
    industry_id = None
    if industry:
        industry_id = (await channel_for_slug(industry)).id
    sources = await sources_repo.list_sources(industry_id, include_disabled=True)
    data = [source_dto(source, admin=True) for source in sources]
    # R10: why a source is not moving — the streak lives in Postgres, the
    # cooldown lives in the Redis host ledger, and the operator needs both.
    ledger = HostLedger()
    cooldowns = await ledger.cooldowns(
        (urlsplit(source.feed_url).hostname or "") for source in sources
    )
    for source, payload in zip(sources, data, strict=True):
        state = cooldowns.get(urlsplit(source.feed_url).hostname or "", {})
        until = float(state.get("cooldown_until") or 0)
        payload["cooldown_until"] = (
            datetime.fromtimestamp(until, UTC).isoformat() if until > 0 else None
        )
        payload["cooldown_reason"] = state.get("cooldown_reason") or ""
    return {"data": data}


@router.post("", status_code=201, dependencies=[Depends(admin_mutation)])
async def create_source(payload: SourceCreate, request: Request) -> Any:
    operator = request.state.operator
    channel = await channel_for_slug(payload.industry)
    language = validate_language(payload.language)
    feed_url = validate_url(payload.feed_url, payload.allow_http)
    source = await sources_repo.create_source(
        industry_id=channel.id,
        name=payload.name,
        feed_url=feed_url,
        language=language,
        trust=payload.trust,
        enabled=payload.enabled,
        allow_http=payload.allow_http,
        poll_interval_min=payload.poll_interval_min,
        terms_checked_at=payload.terms_checked_at.isoformat() if payload.terms_checked_at else None,
        terms_url=payload.terms_url,
    )
    if not source:
        raise Conflict("A source with this feed URL already exists for this channel.")
    await record_audit(
        actor=operator["email"],
        action="source.create",
        entity="source",
        entity_id=source.id,
        payload={"industry": channel.slug, "language": language},
    )
    return {"data": source_dto(source, admin=True)}


@router.patch("/{source_id}", dependencies=[Depends(admin_mutation)])
async def update_source(source_id: str, payload: SourceUpdate, request: Request) -> Any:
    operator = request.state.operator
    source = await sources_repo.get_source(source_id)
    if not source:
        raise NotFound("Source not found.")
    fields = payload.model_dump(exclude_unset=True)
    if "language" in fields and fields["language"] is not None:
        fields["language"] = validate_language(fields["language"])
    if "feed_url" in fields and fields["feed_url"] is not None:
        allow_http = fields.get("allow_http", source.allow_http)
        fields["feed_url"] = validate_url(fields["feed_url"], bool(allow_http))
    if "terms_checked_at" in fields and fields["terms_checked_at"] is not None:
        fields["terms_checked_at"] = fields["terms_checked_at"].isoformat()
    updated = await sources_repo.update_source(source_id, fields)
    if not updated:
        raise NotFound("Source not found.")
    await record_audit(
        actor=operator["email"],
        action="source.update",
        entity="source",
        entity_id=source_id,
        payload={"fields": sorted(fields.keys())},
    )
    return {"data": source_dto(updated, admin=True)}


@router.delete(
    "/{source_id}",
    status_code=204,
    response_model=None,
    response_class=Response,
    dependencies=[Depends(admin_mutation)],
)
async def delete_source(source_id: str, request: Request) -> None:
    operator = request.state.operator
    if not await sources_repo.delete_source(source_id):
        raise NotFound("Source not found.")
    await record_audit(
        actor=operator["email"], action="source.delete", entity="source", entity_id=source_id
    )


@router.post("/{source_id}/test", dependencies=[Depends(admin_mutation)])
async def test_source(source_id: str, request: Request) -> Any:
    source = await sources_repo.get_source(source_id)
    if not source:
        raise NotFound("Source not found.")
    outcome = await fetch_source(source)
    operator = request.state.operator
    await record_audit(
        actor=operator["email"],
        action="source.test",
        entity="source",
        entity_id=source_id,
        payload={"status": outcome.status, "items": len(outcome.items)},
    )
    return {
        "data": {
            "status": outcome.status,
            "item_count": len(outcome.items),
            "error": outcome.error,
            "sample": [{"title": item.title, "url": item.link} for item in outcome.items[:5]],
        }
    }


@router.post("/{source_id}/force-fetch", status_code=202, dependencies=[Depends(admin_mutation)])
async def force_fetch(source_id: str, request: Request) -> Any:
    source = await sources_repo.get_source(source_id)
    if not source:
        raise NotFound("Source not found.")
    channel = await channels_repo.get_channel_by_id(source.industry_id)
    if not channel:
        raise NotFound("Source channel not found.")
    run_id = await create_run(
        channel.id, trigger="manual", requested_by=request.state.operator["email"]
    )
    await enqueue(run_id=run_id, industry=channel.slug, trigger="manual")
    await record_audit(
        actor=request.state.operator["email"],
        action="source.force_fetch",
        entity="source",
        entity_id=source_id,
        payload={"run_id": run_id},
    )
    return {"run_id": run_id, "status": "queued"}


def json_dumps(value: Any) -> str:
    return json.dumps(value, default=str)
