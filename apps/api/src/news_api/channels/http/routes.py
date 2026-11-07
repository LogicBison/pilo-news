from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request

from news_api.channels.domain.theme import Channel
from news_api.channels.infrastructure import repo
from news_api.dependencies import public_access, reject_unknown_query, request_id_of
from news_api.platform.errors import NotFound
from news_api.platform.http_cache import render_json
from news_api.platform.i18n import normalize_locale
from news_api.publishing.application.read_models import base_meta, envelope

router = APIRouter(prefix="/v1", tags=["industries"])


def desk_summary(channel: Channel, latest_published_at: str | None) -> dict[str, Any]:
    """The lobby's shape of a channel: everything the directory and the board
    need in one row, and nothing that belongs to a single locale only."""
    return {
        "slug": channel.slug,
        "name": channel.name,
        "tagline": channel.tagline,
        "locales": channel.locales,
        "accent": channel.theme.get("primary"),
        "layout": channel.theme.get("layout"),
        "offers": channel.effective_offers,
        "fetch_interval_minutes": channel.fetch_interval_minutes,
        "latest_published_at": latest_published_at,
    }


def channel_summary(channel: Channel) -> dict[str, Any]:
    return {
        "slug": channel.slug,
        "name": channel.name,
        "code": channel.code,
        "locales": channel.locales,
        "theme_summary": channel.theme_summary,
    }


def channel_detail(channel: Channel, locale: str) -> dict[str, Any]:
    return {
        "slug": channel.slug,
        "name": channel.name,
        "code": channel.code,
        "tagline": channel.tagline,
        "locales": channel.locales,
        "theme": channel.theme,
        "theme_summary": channel.theme_summary,
        "disclaimer": channel.disclaimer(locale),
        "disclaimers": channel.disclaimers,
        "cta": channel.cta,
        "offers": channel.effective_offers,
        "timezone": channel.timezone,
    }


@router.get("/desks", dependencies=[Depends(public_access)])
async def list_desks(request: Request) -> Any:
    """One round trip for the apex lobby: every desk with its address, tagline,
    live offers and the date of its newest published story."""
    reject_unknown_query(request, {"locale"})
    locale = normalize_locale(request.query_params.get("locale"))
    channels = await repo.list_channels(locale, enabled_only=True)
    latest = await repo.latest_published_by_industry()
    body = envelope(
        [desk_summary(channel, latest.get(channel.slug)) for channel in channels],
        base_meta(
            request_id=request_id_of(request), locale=locale, language=locale, fallback=False
        ),
    )
    return render_json(request, body)


@router.get("/industries", dependencies=[Depends(public_access)])
async def list_industries(request: Request) -> Any:
    reject_unknown_query(request, {"locale"})
    locale = normalize_locale(request.query_params.get("locale"))
    channels = await repo.list_channels(locale, enabled_only=True)
    body = envelope(
        [channel_summary(channel) for channel in channels],
        base_meta(
            request_id=request_id_of(request), locale=locale, language=locale, fallback=False
        ),
    )
    return render_json(request, body)


@router.get("/industries/{slug}", dependencies=[Depends(public_access)])
async def get_industry(slug: str, request: Request) -> Any:
    reject_unknown_query(request, {"locale"})
    locale = normalize_locale(request.query_params.get("locale"))
    channel = await repo.get_channel(slug, locale, enabled_only=True)
    if not channel:
        raise NotFound(f"No industry with slug '{slug}'.")
    body = envelope(
        channel_detail(channel, locale),
        base_meta(
            request_id=request_id_of(request), locale=locale, language=locale, fallback=False
        ),
    )
    return render_json(request, body)
