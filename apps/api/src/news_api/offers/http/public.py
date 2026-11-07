from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Request

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import public_access, reject_unknown_query, request_id_of
from news_api.offers.infrastructure.repo import get_published, list_published
from news_api.platform.errors import InvalidQuery, NotFound
from news_api.platform.http_cache import render_json
from news_api.platform.i18n import normalize_locale
from news_api.publishing.application.read_models import base_meta, envelope

router = APIRouter(prefix="/v1/industries", tags=["references"])


def _summary(row: dict[str, Any]) -> dict[str, Any]:
    issue_date = row["issue_date"]
    return {
        "issue_date": issue_date.isoformat()
        if hasattr(issue_date, "isoformat")
        else str(issue_date),
        "title": row["title"],
        "scope": row["scope"],
        "reviewer": row.get("reviewer"),
        "published_at": row.get("published_at"),
        "row_count": len(row.get("items") or []),
        "standfirst": row.get("standfirst") or "",
        "language": "en",
    }


def _detail(row: dict[str, Any]) -> dict[str, Any]:
    payload = _summary(row)
    payload.update(
        {
            "items": row.get("items") or [],
            "sources": row.get("sources") or [],
            "source_version": row.get("source_version"),
        }
    )
    return payload


async def _channel(slug: str) -> Any:
    channel = await channels_repo.get_channel(slug, enabled_only=True)
    if not channel:
        raise NotFound(f"No industry with slug '{slug}'.")
    return channel


@router.get("/{slug}/references", dependencies=[Depends(public_access)])
async def list_references(slug: str, request: Request) -> Any:
    reject_unknown_query(request, {"locale"})
    locale = normalize_locale(request.query_params.get("locale"))
    channel = await _channel(slug)
    rows = await list_published(channel.id, limit=50)
    body = envelope(
        [_summary(row) for row in rows],
        base_meta(
            request_id=request_id_of(request),
            locale=locale,
            language="en",
            fallback=locale == "es",
        ),
    )
    return render_json(request, body)


@router.get("/{slug}/references/{issue_date}", dependencies=[Depends(public_access)])
async def get_reference(slug: str, issue_date: str, request: Request) -> Any:
    reject_unknown_query(request, {"locale"})
    locale = normalize_locale(request.query_params.get("locale"))
    try:
        parsed = date.fromisoformat(issue_date)
    except ValueError as exc:
        raise InvalidQuery("issue_date must be YYYY-MM-DD.") from exc
    channel = await _channel(slug)
    row = await get_published(channel.id, parsed)
    if not row:
        raise NotFound("Reference issue not found.")
    body = envelope(
        _detail(row),
        base_meta(
            request_id=request_id_of(request),
            locale=locale,
            language="en",
            fallback=locale == "es",
        ),
    )
    return render_json(request, body)
