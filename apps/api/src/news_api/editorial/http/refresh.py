from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from news_api.articles.application.queue import enqueue
from news_api.articles.infrastructure.repo import (
    active_run,
    create_run,
    get_run,
    update_run,
)
from news_api.channels.infrastructure import repo as channels_repo
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform.cache import get_json, lock_holder, set_json
from news_api.platform.db import fetch_all
from news_api.platform.errors import NotFound, RefreshInProgress, ValidationProblem
from news_api.platform.metrics import REFRESH_MANUAL

router = APIRouter(prefix="/v1/admin/refresh", tags=["admin"])


class RefreshRequest(BaseModel):
    industry: str = Field(default="all", min_length=2, max_length=40)
    force: bool = True
    full_reset: bool = False
    confirmation: str | None = Field(default=None, max_length=40)


def run_dto(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": str(run["id"]),
        "industry": run.get("industry_slug"),
        "trigger": run.get("trigger"),
        "status": run.get("status"),
        "started_at": run.get("started_at"),
        "finished_at": run.get("finished_at"),
        "stats": run.get("stats") or {},
    }


@router.post("", status_code=202, dependencies=[Depends(admin_mutation)])
async def trigger_refresh(payload: RefreshRequest, request: Request) -> Any:
    operator = request.state.operator
    idempotency_key = request.headers.get("idempotency-key")
    if idempotency_key:
        cached = await get_json(f"idem:refresh:{idempotency_key}")
        if cached:
            return cached
    if payload.full_reset and payload.confirmation != "RESET":
        raise ValidationProblem("full_reset requires confirmation: 'RESET'.")

    if payload.industry == "all":
        channels = await channels_repo.list_channels(enabled_only=True)
    else:
        channel = await channels_repo.get_channel(payload.industry, enabled_only=True)
        if not channel:
            raise NotFound(f"No industry with slug '{payload.industry}'.")
        channels = [channel]

    for channel in channels:
        active = await active_run(channel.id)
        if active or await lock_holder(f"ingest:lock:{channel.slug}"):
            run_id = str(active["id"]) if active else None
            raise RefreshInProgress(
                "A refresh is already running for this channel.",
                headers={"X-Active-Run": run_id or ""},
            )

    trigger = "reset" if payload.full_reset else "manual"
    runs = []
    for channel in channels:
        run_id = await create_run(
            channel.id, trigger=trigger, requested_by=operator["email"], status="queued"
        )
        await enqueue(
            run_id=run_id,
            industry=channel.slug,
            trigger=trigger,
            full_reset=payload.full_reset,
        )
        REFRESH_MANUAL.labels(industry=channel.slug).inc()
        await record_audit(
            actor=operator["email"],
            action="refresh.trigger",
            entity="refresh_run",
            entity_id=run_id,
            payload={
                "industry": channel.slug,
                "trigger": trigger,
                "full_reset": payload.full_reset,
            },
        )
        runs.append({"run_id": run_id, "industry": channel.slug, "status": "queued"})

    body = {
        "run_id": runs[0]["run_id"],
        "run_ids": [item["run_id"] for item in runs],
        "status": "queued",
        "runs": runs,
    }
    if idempotency_key:
        await set_json(f"idem:refresh:{idempotency_key}", body, ttl_seconds=86400)
    return body


@router.get("", dependencies=[Depends(admin_auth)])
async def list_runs(limit: int = 20) -> Any:
    rows = await fetch_all(
        """
        SELECT r.*, i.slug AS industry_slug FROM refresh_runs r
        LEFT JOIN industries i ON i.id = r.industry_id
        ORDER BY r.started_at DESC LIMIT :limit
        """,
        {"limit": min(max(limit, 1), 100)},
    )
    for row in rows:
        if isinstance(row.get("stats"), str):
            import json

            row["stats"] = json.loads(row["stats"])
    return {"data": [run_dto(row) for row in rows]}


@router.get("/{run_id}", dependencies=[Depends(admin_auth)])
async def refresh_status(run_id: str) -> Any:
    run = await get_run(run_id)
    if not run:
        raise NotFound("Refresh run not found.")
    return {"data": run_dto(run)}


@router.post("/{run_id}/cancel", dependencies=[Depends(admin_mutation)])
async def cancel_run(run_id: str, request: Request) -> Any:
    run = await get_run(run_id)
    if not run:
        raise NotFound("Refresh run not found.")
    if run["status"] in ("queued", "running"):
        await update_run(run_id, status="failed", stats={**run["stats"], "cancelled": True})
        await record_audit(
            actor=request.state.operator["email"],
            action="refresh.cancel",
            entity="refresh_run",
            entity_id=run_id,
        )
    return {"status": "cancelled"}
