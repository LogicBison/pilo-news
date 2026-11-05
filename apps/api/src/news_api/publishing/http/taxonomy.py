from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import public_access, reject_unknown_query, request_id_of
from news_api.platform.errors import InvalidQuery, NotFound
from news_api.platform.http_cache import render_json
from news_api.platform.i18n import normalize_locale
from news_api.publishing.application import read_models

router = APIRouter(prefix="/v1", tags=["taxonomy"])


async def _channel(request: Request) -> Any:
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


@router.get("/topics", dependencies=[Depends(public_access)])
async def list_topics(request: Request) -> Any:
    reject_unknown_query(request, {"industry", "locale"})
    channel = await _channel(request)
    body = await read_models.topics(
        channel,
        locale=normalize_locale(request.query_params.get("locale")),
        request_id=request_id_of(request),
    )
    return render_json(request, body)


@router.get("/sources", dependencies=[Depends(public_access)])
async def list_sources(request: Request) -> Any:
    reject_unknown_query(request, {"industry", "locale"})
    channel = await _channel(request)
    body = await read_models.sources(
        channel,
        locale=normalize_locale(request.query_params.get("locale")),
        request_id=request_id_of(request),
    )
    return render_json(request, body)
