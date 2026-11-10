"""The one outbound door: count the reader leaving, then send them on.

Every "read the full story" link goes through here so the product can answer a
publisher's first question with a number. Aggregate only — one integer per
article, no reader identifier, no IP, no user agent — and never a link the desk
would not show anyway: hidden and archived stories 404.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from news_api.articles.infrastructure import repo as articles_repo
from news_api.platform.errors import NotFound

router = APIRouter(prefix="/v1", tags=["outbound"])


@router.get("/outbound/{article_id}", response_class=RedirectResponse)
async def outbound(article_id: uuid.UUID) -> RedirectResponse:
    target = await articles_repo.record_outbound_click(str(article_id))
    if not target:
        raise NotFound(f"No published story with id '{article_id}'.")
    return RedirectResponse(
        target,
        status_code=302,
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
