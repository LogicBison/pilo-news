from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from news_api.channels.domain.offers import (
    OFFER_KEYS,
    default_offers,
    merge_offers,
    validate_offers,
)
from news_api.channels.domain.theme import DEFAULT_THEMES, is_reserved_slug, validate_theme
from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform.errors import Conflict, NotFound, ValidationProblem
from news_api.platform.i18n import SUPPORTED_LOCALES
from news_api.platform.settings import get_settings

router = APIRouter(prefix="/v1/admin/industries", tags=["admin"])


class LocaleCopy(BaseModel):
    name: str | None = None
    tagline: str | None = None


class TopicSeed(BaseModel):
    slug: str = Field(pattern="^[a-z0-9-]{2,40}$")
    label: dict[str, str] = Field(default_factory=dict)
    weight: float = Field(default=1.0, gt=0, le=10)
    keywords: dict[str, list[str]] = Field(default_factory=dict)


class IndustryCreate(BaseModel):
    slug: str = Field(pattern="^[a-z0-9-]{2,40}$")
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    theme: dict[str, Any] | None = None
    locales: dict[str, LocaleCopy] | None = None
    disclaimers: dict[str, str] | None = None
    cta: dict[str, Any] = Field(default_factory=dict)
    timezone: str = Field(default="America/El_Salvador", max_length=64)
    retention_days: int = Field(default=7, ge=1, le=90)
    sort_order: int = Field(default=100, ge=0, le=10000)
    enabled: bool = True
    fetch_interval_minutes: int | None = Field(default=None, ge=5, le=1440)
    auto_fetch_enabled: bool = True
    ai_summaries_enabled: bool = True
    offers: dict[str, bool] | None = None
    topics: list[TopicSeed] = Field(default_factory=list)


class IndustryUpdate(BaseModel):
    enabled: bool | None = None
    theme: dict[str, Any] | None = None
    disclaimers: dict[str, str] | None = None
    retention_days: int | None = Field(default=None, ge=1, le=90)
    fetch_interval_minutes: int | None = Field(default=None, ge=5, le=1440)
    auto_fetch_enabled: bool | None = None
    ai_summaries_enabled: bool | None = None
    offers: dict[str, bool] | None = None


def admin_channel(channel: Any) -> dict[str, Any]:
    default_interval = get_settings().refresh_interval_minutes
    return {
        "slug": channel.slug,
        "name": channel.name,
        "base_name": channel.base_name,
        "code": channel.code,
        "tagline": channel.tagline,
        "locales": channel.locales,
        "theme": channel.theme,
        "disclaimers": channel.disclaimers,
        "cta": channel.cta,
        "asset": channel.cta.get("asset"),
        "offers": channel.effective_offers,
        "timezone": channel.timezone,
        "retention_days": channel.retention_days,
        "enabled": channel.enabled,
        "sort_order": channel.sort_order,
        "fetch_interval_minutes": channel.fetch_interval_minutes,
        "auto_fetch_enabled": channel.auto_fetch_enabled,
        "ai_summaries_enabled": channel.ai_summaries_enabled,
        "effective_fetch_interval_minutes": channel.effective_fetch_interval(default_interval),
    }


def _offers_for_create(cta: dict[str, Any], patch: dict[str, bool] | None) -> dict[str, bool]:
    defaults = default_offers(cta)
    offers = defaults if patch is None else {**defaults, **patch}
    problems = validate_offers(cta, offers)
    if problems:
        raise ValidationProblem("; ".join(problems))
    return {key: bool(offers[key]) for key in OFFER_KEYS}


@router.get("", dependencies=[Depends(admin_auth)])
async def list_industries() -> Any:
    channels = await channels_repo.list_channels(enabled_only=False)
    settings = get_settings()
    return {
        "data": [admin_channel(channel) for channel in channels],
        "defaults": {"fetch_interval_minutes": settings.refresh_interval_minutes},
    }


@router.post("", status_code=201, dependencies=[Depends(admin_mutation)])
async def create_industry(payload: IndustryCreate, request: Request) -> Any:
    if is_reserved_slug(payload.slug):
        raise ValidationProblem("slug is reserved.")
    existing = await channels_repo.get_channel(payload.slug, enabled_only=False)
    if existing:
        raise Conflict("An industry with this slug already exists.")
    theme_input = dict(payload.theme or {})
    layout = str(theme_input.get("layout", "editorial"))
    base = DEFAULT_THEMES.get(layout, DEFAULT_THEMES["editorial"])
    theme = {**base, **theme_input}
    problems = validate_theme(theme)
    if problems:
        raise ValidationProblem("; ".join(problems))
    locales = payload.locales or {
        "en": LocaleCopy(name=payload.name, tagline=""),
        "es": LocaleCopy(name=payload.name, tagline=""),
    }
    unsupported = sorted(set(locales) - set(SUPPORTED_LOCALES))
    if unsupported:
        raise ValidationProblem(f"Unsupported locale(s): {', '.join(unsupported)}.")
    disclaimers = payload.disclaimers or {
        "en": "News, not professional advice.",
        "es": "Noticias, no asesoría profesional.",
    }
    offers = _offers_for_create(payload.cta, payload.offers)
    channel = await channels_repo.create_channel(
        slug=payload.slug,
        code=payload.code,
        name=payload.name,
        theme=theme,
        locales={
            locale: {"name": copy.name or payload.name, "tagline": copy.tagline or ""}
            for locale, copy in locales.items()
        },
        disclaimers=disclaimers,
        cta=payload.cta,
        timezone=payload.timezone,
        retention_days=payload.retention_days,
        sort_order=payload.sort_order,
        enabled=payload.enabled,
        topics=[topic.model_dump() for topic in payload.topics],
        fetch_interval_minutes=payload.fetch_interval_minutes,
        auto_fetch_enabled=payload.auto_fetch_enabled,
        ai_summaries_enabled=payload.ai_summaries_enabled,
        offers=offers,
    )
    if not channel:
        raise Conflict("An industry with this slug already exists.")
    await record_audit(
        actor=request.state.operator["email"],
        action="industry.create",
        entity="industry",
        entity_id=payload.slug,
        payload={"name": payload.name, "locales": sorted(locales.keys())},
    )
    return {"data": admin_channel(channel)}


@router.patch("/{slug}", dependencies=[Depends(admin_mutation)])
async def update_industry(slug: str, payload: IndustryUpdate, request: Request) -> Any:
    existing = await channels_repo.get_channel(slug, enabled_only=False)
    if not existing:
        raise NotFound(f"No industry with slug '{slug}'.")
    if payload.theme is not None:
        problems = validate_theme(payload.theme)
        if problems:
            raise ValidationProblem("; ".join(problems))
    if payload.disclaimers is not None:
        unknown = sorted(set(payload.disclaimers) - set(SUPPORTED_LOCALES))
        if unknown:
            raise ValidationProblem(f"Unsupported disclaimer locale(s): {', '.join(unknown)}.")
    payload_fields = payload.model_fields_set
    offers: dict[str, bool] | None = None
    if "offers" in payload_fields and payload.offers is not None:
        unknown = sorted(set(payload.offers) - set(OFFER_KEYS))
        if unknown:
            raise ValidationProblem(f"unknown offer(s): {', '.join(unknown)}")
        offers = merge_offers(existing.cta, existing.offers, payload.offers)
        problems = validate_offers(existing.cta, offers)
        if problems:
            raise ValidationProblem("; ".join(problems))
    if "fetch_interval_minutes" in payload_fields:
        clear_fetch_interval = payload.fetch_interval_minutes is None
        fetch_interval_minutes = payload.fetch_interval_minutes
    else:
        clear_fetch_interval = False
        fetch_interval_minutes = None
    await channels_repo.update_channel(
        slug,
        enabled=payload.enabled,
        theme=payload.theme,
        disclaimers=payload.disclaimers,
        retention_days=payload.retention_days,
        fetch_interval_minutes=fetch_interval_minutes,
        clear_fetch_interval=clear_fetch_interval,
        auto_fetch_enabled=payload.auto_fetch_enabled,
        ai_summaries_enabled=payload.ai_summaries_enabled,
        offers=offers,
    )
    updated = await channels_repo.get_channel(slug, enabled_only=False)
    await record_audit(
        actor=request.state.operator["email"],
        action="industry.update",
        entity="industry",
        entity_id=slug,
        payload={
            "fields": [
                key
                for key in (
                    "enabled",
                    "theme",
                    "disclaimers",
                    "retention_days",
                    "fetch_interval_minutes",
                    "auto_fetch_enabled",
                    "ai_summaries_enabled",
                    "offers",
                )
                if key in payload_fields
            ]
        },
    )
    return {"data": admin_channel(updated) if updated else None}
