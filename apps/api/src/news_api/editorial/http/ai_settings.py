"""Admin-editable AI cost controls.

The `.env` values are the deployment default; this endpoint is the operator's
live knob. Reads return both, so the console can show "1 (env 20)". Writes are
validated here, stored in `platform_settings`, audited, and visible to every
process within the override TTL.

The read also reports the ledger: today's and this month's requests, tokens and
dollars against every cap, and whether the stack is halted. A halt is the kill
switch - a rejected key or an open circuit breaker - and only `resume` clears
it, so a stopped stack stays stopped until a human says otherwise.
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

# Pairs that must stay in order: a daily cap above the monthly one would let the
# month bind first and make the daily knob decorative.
_NESTED_LIMITS = (
    ("ai_daily_token_limit", "ai_monthly_token_limit"),
    ("ai_daily_request_limit", "ai_monthly_request_limit"),
    ("ai_daily_budget_usd", "ai_monthly_budget_usd"),
)


class AISettingsUpdate(BaseModel):
    """Every field is optional: absent keeps, explicit null clears to `.env`."""

    reset: bool = False
    ai_enabled: bool | None = None
    ai_daily_token_limit: int | None = Field(default=None, ge=1, le=1_000_000_000)
    ai_monthly_token_limit: int | None = Field(default=None, ge=1, le=1_000_000_000)
    ai_daily_request_limit: int | None = Field(default=None, ge=1, le=10_000_000)
    ai_monthly_request_limit: int | None = Field(default=None, ge=1, le=10_000_000)
    ai_daily_budget_usd: float | None = Field(default=None, gt=0, le=1000)
    ai_monthly_budget_usd: float | None = Field(default=None, gt=0, le=1000)
    ai_max_items_per_run: int | None = Field(default=None, ge=1, le=500)
    ai_desks_per_tick: int | None = Field(default=None, ge=1, le=100)
    ai_rotation_minutes: int | None = Field(default=None, ge=0, le=1440)
    ai_offpeak_only: bool | None = None
    ai_peak_windows: str | None = Field(default=None, max_length=200)
    ai_peak_days: str | None = Field(default=None, max_length=40)
    ai_peak_holidays: str | None = Field(default=None, max_length=1000)


def _defaults() -> dict[str, Any]:
    settings = get_settings()
    return {
        "ai_enabled": settings.ai_enabled,
        "ai_daily_token_limit": settings.ai_daily_token_limit,
        "ai_monthly_token_limit": settings.ai_monthly_token_limit,
        "ai_daily_request_limit": settings.ai_daily_request_limit,
        "ai_monthly_request_limit": settings.ai_monthly_request_limit,
        "ai_daily_budget_usd": settings.ai_daily_budget_usd,
        "ai_monthly_budget_usd": settings.ai_monthly_budget_usd,
        "ai_max_items_per_run": settings.ai_max_items_per_run,
        "ai_desks_per_tick": settings.ai_desks_per_tick,
        "ai_rotation_minutes": settings.ai_rotation_minutes,
        "ai_offpeak_only": settings.ai_offpeak_only,
        "ai_peak_windows": settings.ai_peak_windows,
        "ai_peak_days": settings.ai_peak_days,
        "ai_peak_holidays": settings.ai_peak_holidays,
    }


def _limits(values: dict[str, Any]) -> ai_budget.Limits:
    return ai_budget.Limits(
        daily_tokens=int(values["ai_daily_token_limit"]),
        monthly_tokens=int(values["ai_monthly_token_limit"]),
        daily_requests=int(values["ai_daily_request_limit"]),
        monthly_requests=int(values["ai_monthly_request_limit"]),
        daily_usd=float(values["ai_daily_budget_usd"]),
        monthly_usd=float(values["ai_monthly_budget_usd"]),
    )


async def _payload() -> dict[str, Any]:
    defaults = _defaults()
    stored = await overrides.stored()
    applied = stored.get("values") or {}
    values = {**defaults, **applied}
    ledger_ok = True
    try:
        ledger = await ai_budget.snapshot(_limits(values))
    except ai_budget.BudgetUnavailable:
        ledger_ok = False
        ledger = {"day": None, "month": None, "halted_reason": None, "halted_until": None}
    month = ledger.get("month") or {}
    month_remaining = month.get("remaining") or {}
    return {
        "data": {
            "values": values,
            "defaults": defaults,
            "overridden": sorted(applied),
            "updated_at": stored.get("updated_at"),
            "updated_by": stored.get("updated_by"),
            "ledger": ledger,
            "halted_reason": ledger.get("halted_reason"),
            "halted_until": ledger.get("halted_until"),
            # Kept flat too: the panel's headline numbers, and the shape the
            # OpenAPI snapshot and the existing contract tests already assert.
            "spent_usd": month.get("cost_usd", 0.0),
            "held_usd": month.get("held_usd", 0.0),
            "remaining_usd": month_remaining.get("usd", 0.0),
            "bucket": month.get("bucket") or ai_budget.monthly_bucket(),
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


async def _validate(patch: dict[str, Any]) -> dict[str, Any]:
    """Canonicalise the calendar and keep every daily cap inside its monthly one."""
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
    # A null clears the override, so what will be in force is the `.env`
    # default: compare against the merged result, not against the stored row.
    effective = {**_defaults(), **(await overrides.load())}
    for key, value in cleaned.items():
        if value is not None:
            effective[key] = value
    for daily_key, monthly_key in _NESTED_LIMITS:
        daily, monthly = effective.get(daily_key), effective.get(monthly_key)
        if daily is None or monthly is None:
            continue
        if float(daily) > float(monthly):
            raise ValidationProblem(f"{daily_key} cannot be above {monthly_key}")
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
        await overrides.save(await _validate(patch), updated_by=actor)
        action_fields = sorted(patch)
    await record_audit(
        actor=actor,
        action="ai.settings.update",
        entity="platform_settings",
        entity_id="ai",
        payload={"fields": action_fields},
    )
    return await _payload()


@router.post("/resume", dependencies=[Depends(admin_mutation)])
async def resume_ai(request: Request) -> Any:
    """Clear a halt so the stack may call the provider again.

    Deliberately explicit. A halt means the key was rejected or the provider
    failed repeatedly; clearing it is an operator decision, not a retry policy,
    and the audit row records which reason was cleared.
    """
    actor = request.state.operator["email"]
    limits = _limits({**_defaults(), **(await overrides.load())})
    try:
        state = await ai_budget.snapshot(limits)
    except ai_budget.BudgetUnavailable as exc:
        raise ValidationProblem("the usage ledger is unreadable; cannot resume") from exc
    await ai_budget.resume(by=actor)
    await record_audit(
        actor=actor,
        action="ai.halt.resume",
        entity="platform_settings",
        entity_id="ai",
        payload={"cleared": state.get("halted_reason")},
    )
    return await _payload()
