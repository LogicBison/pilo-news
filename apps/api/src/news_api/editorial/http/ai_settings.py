"""Admin-editable AI cost controls.

The `.env` values are the deployment default; this endpoint is the operator's
live knob. Reads return both, so the console can show "1 (env 20)". Writes are
validated here, stored in `platform_settings`, audited, and visible to every
process within the override TTL.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from news_api.articles.infrastructure import ai_budget
from news_api.dependencies import admin_auth, admin_mutation
from news_api.editorial.infrastructure.repo import record_audit
from news_api.platform import overrides
from news_api.platform.config import scoring_config
from news_api.platform.errors import ValidationProblem
from news_api.platform.offpeak import parse_peak_days, parse_peak_holidays, parse_peak_windows
from news_api.platform.settings import get_settings

router = APIRouter(prefix="/v1/admin/ai", tags=["admin"])


class AISettingsUpdate(BaseModel):
    """Every field is optional: absent keeps, explicit null clears to `.env`."""

    reset: bool = False
    ai_enabled: bool | None = None
    ai_monthly_budget_usd: float | None = Field(default=None, gt=0, le=1000)
    ai_max_items_per_run: int | None = Field(default=None, ge=1, le=500)
    ai_offpeak_only: bool | None = None
    ai_peak_windows: str | None = Field(default=None, max_length=200)
    ai_peak_days: str | None = Field(default=None, max_length=40)
    ai_peak_holidays: str | None = Field(default=None, max_length=1000)


def _defaults() -> dict[str, Any]:
    settings = get_settings()
    return {
        "ai_enabled": settings.ai_enabled,
        "ai_monthly_budget_usd": settings.ai_monthly_budget_usd,
        "ai_max_items_per_run": settings.ai_max_items_per_run,
        "ai_offpeak_only": settings.ai_offpeak_only,
        "ai_peak_windows": settings.ai_peak_windows,
        "ai_peak_days": settings.ai_peak_days,
        "ai_peak_holidays": settings.ai_peak_holidays,
    }


async def _payload() -> dict[str, Any]:
    defaults = _defaults()
    stored = await overrides.stored()
    applied = stored.get("values") or {}
    values = {**defaults, **applied}
    ledger_ok = True
    try:
        spent, held = await ai_budget.spent_and_held()
    except ai_budget.BudgetUnavailable:
        ledger_ok = False
        spent, held = 0.0, 0.0
    budget = float(values["ai_monthly_budget_usd"])
    return {
        "data": {
            "values": values,
            "defaults": defaults,
            "overridden": sorted(applied),
            "updated_at": stored.get("updated_at"),
            "updated_by": stored.get("updated_by"),
            "spent_usd": round(spent, 6),
            "held_usd": round(held, 6),
            "remaining_usd": round(max(0.0, budget - spent - held), 6),
            "bucket": ai_budget.monthly_bucket(),
            "ledger_available": ledger_ok,
            "pricing": {
                key: scoring_config().get("ai", {}).get(key)
                for key in (
                    "input_offpeak_price_per_million",
                    "output_offpeak_price_per_million",
                )
            },
        }
    }


def _validate(patch: dict[str, Any]) -> dict[str, Any]:
    """Canonicalise the calendar fields so the stored row is readable."""
    cleaned = dict(patch)
    if cleaned.get("ai_peak_windows") is not None:
        try:
            parse_peak_windows(str(cleaned["ai_peak_windows"]))
        except ValueError as exc:
            raise ValidationProblem(f"invalid peak windows: {exc}") from exc
    if cleaned.get("ai_peak_days") is not None:
        try:
            parse_peak_days(str(cleaned["ai_peak_days"]))
        except ValueError as exc:
            raise ValidationProblem(f"invalid peak days: {exc}") from exc
    if cleaned.get("ai_peak_holidays") is not None:
        try:
            parse_peak_holidays(str(cleaned["ai_peak_holidays"]))
        except ValueError as exc:
            raise ValidationProblem(f"invalid holidays: {exc}") from exc
    return cleaned


@router.get("", dependencies=[Depends(admin_auth)])
async def read_ai_settings() -> Any:
    return await _payload()


@router.patch("", dependencies=[Depends(admin_mutation)])
async def update_ai_settings(payload: AISettingsUpdate, request: Request) -> Any:
    actor = request.state.operator["email"]
    if payload.reset:
        await overrides.clear(updated_by=actor)
        action_fields = ["reset"]
    else:
        patch = {
            key: getattr(payload, key)
            for key in payload.model_fields_set
            if key in overrides.OVERRIDABLE
        }
        if not patch:
            raise ValidationProblem("no setting supplied")
        await overrides.save(_validate(patch), updated_by=actor)
        action_fields = sorted(patch)
    await record_audit(
        actor=actor,
        action="ai.settings.update",
        entity="platform_settings",
        entity_id="ai",
        payload={"fields": action_fields},
    )
    return await _payload()
