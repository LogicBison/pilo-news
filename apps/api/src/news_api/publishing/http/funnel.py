from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request

from news_api.dependencies import admin_auth
from news_api.platform.db import fetch_all, fetch_one
from news_api.platform.errors import InvalidQuery
from news_api.platform.http_cache import NO_STORE, render_json

router = APIRouter(prefix="/v1/admin/funnel", tags=["admin"])

STAGES = (
    "cta_impression",
    "cta_click",
    "lead_form_start",
    "lead_submit",
    "question_submit",
    "asset_interest",
)


def _days(request: Request) -> int:
    raw = request.query_params.get("days", "30")
    try:
        value = int(raw)
    except ValueError as exc:
        raise InvalidQuery("days must be an integer between 1 and 365.") from exc
    if value < 1 or value > 365:
        raise InvalidQuery("days must be between 1 and 365.")
    return value


@router.get("", dependencies=[Depends(admin_auth)])
async def funnel(request: Request) -> Any:
    """Funnel read-out: CTA events and lead outcomes per channel and placement."""
    days = _days(request)
    industry = request.query_params.get("industry")
    window: dict[str, Any] = {"days": days}
    channel_filter = ""
    if industry:
        channel_filter = " AND i.slug = :industry"
        window["industry"] = industry

    events = await fetch_all(
        f"""
        SELECT i.slug AS industry, e.event, e.placement, count(*)::int AS total
        FROM cta_events e
        JOIN industries i ON i.id = e.industry_id
        WHERE e.created_at >= now() - make_interval(days => :days){channel_filter}
        GROUP BY i.slug, e.event, e.placement
        ORDER BY i.slug, e.event, e.placement
        """,
        window,
    )
    leads = await fetch_all(
        f"""
        SELECT i.slug AS industry, l.kind, l.status, count(*)::int AS total
        FROM leads l
        JOIN industries i ON i.id = l.industry_id
        WHERE l.created_at >= now() - make_interval(days => :days){channel_filter}
        GROUP BY i.slug, l.kind, l.status
        ORDER BY i.slug, l.kind, l.status
        """,
        window,
    )
    totals = await fetch_one(
        f"""
        SELECT
            (SELECT count(*)::int FROM cta_events e JOIN industries i ON i.id = e.industry_id
             WHERE e.created_at >= now() - make_interval(days => :days){channel_filter}) AS events,
            (SELECT count(*)::int FROM leads l JOIN industries i ON i.id = l.industry_id
             WHERE l.created_at >= now() - make_interval(days => :days){channel_filter}) AS leads
        """,
        window,
    )

    channels: dict[str, dict[str, Any]] = {}

    def bucket_for(slug: str) -> dict[str, Any]:
        return channels.setdefault(
            slug,
            {"industry": slug, "events": {}, "placements": {}, "leads": {}},
        )

    for row in events:
        bucket = bucket_for(row["industry"])
        bucket["events"][row["event"]] = row["total"]
        bucket["placements"][row["placement"] or "-"] = (
            bucket["placements"].get(row["placement"] or "-", 0) + row["total"]
        )
    for row in leads:
        bucket = bucket_for(row["industry"])
        bucket["leads"][f"{row['kind']}:{row['status']}"] = row["total"]

    rows = []
    for bucket in sorted(channels.values(), key=lambda item: item["industry"]):
        impressions = bucket["events"].get("cta_impression", 0)
        clicks = bucket["events"].get("cta_click", 0)
        starts = bucket["events"].get("lead_form_start", 0)
        submits = bucket["events"].get("lead_submit", 0)
        submits += bucket["events"].get("question_submit", 0)
        leads_total = sum(bucket["leads"].values())
        rows.append(
            {
                "industry": bucket["industry"],
                "events": bucket["events"],
                "placements": bucket["placements"],
                "leads_by_kind": bucket["leads"],
                "rates": {
                    "click_rate": round(clicks / impressions, 4) if impressions else None,
                    "start_rate": round(starts / clicks, 4) if clicks else None,
                    "submit_rate": round(submits / starts, 4) if starts else None,
                    "lead_rate": round(leads_total / impressions, 4) if impressions else None,
                },
            }
        )

    payload = {
        "window_days": days,
        "industry": industry or "all",
        "stages": list(STAGES),
        "totals": {
            "events": totals["events"] if totals else 0,
            "leads": totals["leads"] if totals else 0,
        },
        "channels": rows,
    }
    return render_json(request, payload, cache_control=NO_STORE)
