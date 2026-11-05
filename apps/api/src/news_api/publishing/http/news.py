from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request

from news_api.channels.domain.theme import Channel
from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import public_access, reject_unknown_query, request_id_of
from news_api.platform.errors import InvalidQuery, NotFound
from news_api.platform.http_cache import render_json
from news_api.platform.i18n import normalize_locale
from news_api.platform.metrics import NEWS_READS
from news_api.platform.pagination import decode_cursor
from news_api.publishing.application import read_models

router = APIRouter(prefix="/v1/news", tags=["news"])
TOPIC_RE = re.compile(r"^[a-z0-9-]{2,40}$")


async def resolve_channel(request: Request) -> Channel:
    reject_unknown_query(
        request,
        {"industry", "locale", "topic", "q", "limit", "cursor"},
    )
    slug = request.query_params.get("industry")
    if not slug:
        channels = await channels_repo.list_channels(enabled_only=True)
        if len(channels) != 1:
            raise InvalidQuery("The 'industry' query parameter is required.")
        return channels[0]
    channel = await channels_repo.get_channel(slug, enabled_only=True)
    if not channel:
        raise NotFound(f"No industry with slug '{slug}'.")
    return channel


def parse_limit(request: Request) -> int:
    raw = request.query_params.get("limit")
    if raw is None:
        return 20
    try:
        value = int(raw)
    except ValueError as exc:
        raise InvalidQuery("limit must be an integer between 1 and 50.") from exc
    if value < 1 or value > 50:
        raise InvalidQuery("limit must be between 1 and 50.")
    return value


@router.get("", dependencies=[Depends(public_access)])
async def list_news(request: Request) -> Any:
    channel = await resolve_channel(request)
    topic = request.query_params.get("topic")
    if topic and not TOPIC_RE.match(topic):
        raise InvalidQuery("topic must match [a-z0-9-]{2,40}.")
    query = request.query_params.get("q")
    if query is not None:
        query = query.strip()
        if len(query) < 3 or len(query) > 64:
            raise InvalidQuery("q must be between 3 and 64 characters.")
    cursor = decode_cursor(request.query_params.get("cursor"))
    cursor_tuple = (cursor.score, cursor.published_at, cursor.article_id) if cursor else None
    body = await read_models.list_page(
        channel,
        locale=normalize_locale(request.query_params.get("locale")),
        limit=parse_limit(request),
        cursor=cursor_tuple,
        topic=topic,
        query=query,
        request_id=request_id_of(request),
    )
    NEWS_READS.labels(
        industry=channel.slug, endpoint="news", language=body["meta"]["language"]
    ).inc()
    return render_json(request, body)


@router.get("/bundle", dependencies=[Depends(public_access)])
async def news_bundle(request: Request) -> Any:
    reject_unknown_query(request, {"industry", "locale"})
    channel = await resolve_channel_for_bundle(request)
    body = await read_models.bundle(
        channel,
        locale=normalize_locale(request.query_params.get("locale")),
        request_id=request_id_of(request),
    )
    NEWS_READS.labels(
        industry=channel.slug, endpoint="bundle", language=body["meta"]["language"]
    ).inc()
    return render_json(request, body)


async def resolve_channel_for_bundle(request: Request) -> Channel:
    slug = request.query_params.get("industry")
    if not slug:
        channels = await channels_repo.list_channels(enabled_only=True)
        if len(channels) != 1:
            raise InvalidQuery("The 'industry' query parameter is required.")
        return channels[0]
    channel = await channels_repo.get_channel(slug, enabled_only=True)
    if not channel:
        raise NotFound(f"No industry with slug '{slug}'.")
    return channel


@router.get("/splash", dependencies=[Depends(public_access)])
async def news_splash(request: Request) -> Any:
    reject_unknown_query(request, {"industry", "locale"})
    channel = await resolve_channel_for_bundle(request)
    body = await read_models.splash(
        channel,
        locale=normalize_locale(request.query_params.get("locale")),
        request_id=request_id_of(request),
    )
    NEWS_READS.labels(
        industry=channel.slug, endpoint="splash", language=body["meta"]["language"]
    ).inc()
    return render_json(request, body)


@router.get("/{article_id}", dependencies=[Depends(public_access)])
async def article_detail(article_id: str, request: Request) -> Any:
    reject_unknown_query(request, {"industry", "locale"})
    try:
        uuid.UUID(article_id)
    except ValueError as exc:
        raise NotFound("Article not found.") from exc
    channel = await resolve_channel_for_bundle(request)
    body = await read_models.article_detail(
        channel,
        locale=normalize_locale(request.query_params.get("locale")),
        article_id=article_id,
        request_id=request_id_of(request),
    )
    if not body:
        raise NotFound("Article not found.")
    NEWS_READS.labels(
        industry=channel.slug, endpoint="article", language=body["meta"]["language"]
    ).inc()
    return render_json(request, body)
