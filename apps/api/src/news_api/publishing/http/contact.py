from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import client_country, client_ip, public_access
from news_api.platform.cache import rate_limit
from news_api.platform.errors import RateLimited, ValidationProblem
from news_api.platform.metrics import CONTACT_RATE_LIMITED, CONTACT_SUBMISSIONS
from news_api.platform.notify import notify_contact
from news_api.platform.settings import get_settings
from news_api.platform.utm import normalize_utm
from news_api.publishing.application import leads as leads_app
from news_api.publishing.infrastructure import repo

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["contact"])


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    message: str = Field(min_length=10, max_length=2000)
    locale: str = Field(default="en", max_length=10)
    industry: str | None = Field(default=None, max_length=40)
    source_page: str | None = Field(default=None, max_length=300)
    utm: dict[str, str] | None = None
    session_hash: str | None = Field(default=None, max_length=120)
    website: str | None = Field(default=None, max_length=200)  # honeypot


@router.post("/contact", dependencies=[Depends(public_access)])
async def submit_contact(payload: ContactRequest, request: Request) -> Any:
    if payload.website:
        return {"status": "received"}
    settings = get_settings()
    industry_id = None
    slug = payload.industry
    if slug:
        channel = await channels_repo.get_channel(slug, enabled_only=True)
        if not channel:
            raise ValidationProblem("Unknown industry.")
        industry_id = channel.id
    allowed, _, reset = await rate_limit(
        f"contact:{client_ip(request)}", settings.contact_rate_limit_per_hour, 3600
    )
    if not allowed:
        CONTACT_RATE_LIMITED.labels(industry=slug or "-").inc()
        headers = {"Retry-After": str(max(1, reset - int(__import__("time").time())))}
        raise RateLimited("Too many messages. Try again later.", headers=headers)
    duplicate = await repo.recent_contact_count(industry_id, str(payload.email), minutes=10)
    if duplicate:
        CONTACT_SUBMISSIONS.labels(industry=slug or "-", result="duplicate").inc()
        return {"status": "received"}
    ip_hash, ua_hash = leads_app.ip_and_ua_hash(
        client_ip(request), request.headers.get("user-agent", "")
    )
    contact_id = await repo.insert_contact(
        industry_id=industry_id,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        message=payload.message,
        locale=payload.locale,
        source_page=payload.source_page,
        utm=normalize_utm(payload.utm),
        ip_hash=ip_hash,
        ua_hash=ua_hash,
        country=client_country(request),
        session_hash=leads_app.session_hash_value(payload.session_hash),
    )
    CONTACT_SUBMISSIONS.labels(industry=slug or "-", result="ok").inc()
    await notify_contact(
        industry=slug,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        message=payload.message,
    )
    log.info("contact.received", industry=slug or "-", contact_id=contact_id)
    return {"id": contact_id}
