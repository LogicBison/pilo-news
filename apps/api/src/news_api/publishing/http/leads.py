from __future__ import annotations

import time
from typing import Any, Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr, Field

from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import client_country, client_ip, public_access
from news_api.platform.cache import rate_limit
from news_api.platform.errors import NotFound, RateLimited
from news_api.platform.metrics import LEADS_RATE_LIMITED
from news_api.platform.settings import get_settings
from news_api.publishing.application import leads as leads_app

router = APIRouter(prefix="/v1", tags=["leads"])


class LeadRequest(BaseModel):
    industry: str = Field(min_length=2, max_length=40)
    kind: Literal["consultation", "brief", "question", "asset"] = "consultation"
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    company: str | None = Field(default=None, max_length=120)
    message: str | None = Field(default=None, max_length=2000)
    qualification: str | None = Field(default=None, max_length=60)
    asset: str | None = Field(default=None, max_length=60)
    locale: str = Field(default="en", max_length=10)
    consent: bool = False
    source_page: str | None = Field(default=None, max_length=300)
    article_id: str | None = Field(default=None, max_length=36)
    utm: dict[str, str] | None = None
    session_hash: str | None = Field(default=None, max_length=120)
    website: str | None = Field(default=None, max_length=200)  # honeypot


@router.post("/leads", dependencies=[Depends(public_access)])
async def create_lead(payload: LeadRequest, request: Request) -> Any:
    if payload.website:
        return {"status": "received"}
    settings = get_settings()
    channel = await channels_repo.get_channel(payload.industry, enabled_only=True)
    if not channel:
        raise NotFound("Unknown industry.")
    allowed, _, reset = await rate_limit(
        f"lead:{client_ip(request)}", settings.lead_rate_limit_per_hour, 3600
    )
    if not allowed:
        LEADS_RATE_LIMITED.labels(industry=channel.slug).inc()
        raise RateLimited(
            "Too many submissions. Try again later.",
            headers={"Retry-After": str(max(1, reset - int(time.time())))},
        )
    ip_hash, ua_hash = leads_app.ip_and_ua_hash(
        client_ip(request), request.headers.get("user-agent", "")
    )
    lead_id, duplicate, partner = await leads_app.create_lead(
        channel,
        {
            "kind": payload.kind,
            "name": payload.name,
            "email": str(payload.email),
            "phone": payload.phone,
            "company": payload.company,
            "message": payload.message,
            "qualification": payload.qualification,
            "asset": payload.asset,
            "locale": payload.locale,
            "consent": payload.consent,
            "source_page": payload.source_page,
            "article_id": payload.article_id,
            "utm": payload.utm or {},
        },
        ip_hash=ip_hash,
        ua_hash=ua_hash,
        country=client_country(request),
        session_hash=leads_app.session_hash_value(payload.session_hash),
    )
    body = leads_app.lead_public_response(lead_id, duplicate)
    if partner and not duplicate:
        body["status"] = "received"
    return body
