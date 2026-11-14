"""Global AI limits: reserve -> call -> settle, fail closed, durable.

Two buckets are kept at once - the UTC day and the UTC month - and each counts
what the provider bills (requests, tokens) next to the dollar estimate this
stack derives from ``config/scoring.json``. A call is allowed only when it fits
**both** buckets on **all three** dimensions, so a wrong price can no longer
silently raise the real ceiling: the token and request caps hold regardless.

The rows live in Postgres, not Redis. A Redis-only ledger disappeared with the
volume - a ``destroy``, a lost volume or a dev->prd restore started the month
at zero spent - and it could not bound a single day inside the month. These
rows survive all three, and one row per day is an audit trail an operator can
read after the fact.

Reserve books the worst case before the request; settle replaces it with the
provider's reported usage. An unknown outcome (timeout, unparsable 200) keeps
the worst case, because the provider may have billed it. A ledger this stack
cannot read or write **denies** the call: a blank ledger is not a free pass.

``halt`` is the kill switch for outcomes that are not about money. A 401/403
means the key is wrong or the account is stopped, and retrying cannot help; an
auth halt has no expiry and only an operator resume clears it. A circuit
breaker halt expires by itself.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import text

from news_api.platform.clock import utcnow
from news_api.platform.config import scoring_config
from news_api.platform.db import session_scope

log = structlog.get_logger(__name__)

# Used only to size a run's allowance, never for accounting.
_PLANNING_PROMPT_TOKENS = 400
_PLANNING_OUTPUT_TOKENS = 160
# Tokenizers differ; three characters per token with a 5% margin is a
# deliberately pessimistic count. Over-reserving only delays the next call -
# it never lets one through.
_CHARS_PER_TOKEN = 3
_SAFETY = 1.05
_EPSILON = 1e-9


class BudgetExceeded(Exception):
    """A cap would be crossed, or the bucket is halted."""

    def __init__(self, message: str, *, reason: str = "cap") -> None:
        super().__init__(message)
        self.reason = reason


class BudgetUnavailable(Exception):
    """The ledger cannot be trusted right now, so no money is spent."""


@dataclass(frozen=True)
class Limits:
    """The caps in force: `.env` defaults with the admin row on top."""

    daily_tokens: int
    monthly_tokens: int
    daily_requests: int
    monthly_requests: int
    daily_usd: float
    monthly_usd: float

    def for_bucket(self, kind: str) -> tuple[int, int, float]:
        """(requests, tokens, usd) for one bucket kind."""
        if kind == "day":
            return self.daily_requests, self.daily_tokens, self.daily_usd
        return self.monthly_requests, self.monthly_tokens, self.monthly_usd


@dataclass(frozen=True)
class Estimate:
    """Worst case for one call, reserved before it is sent."""

    tokens: int
    usd: float


@dataclass(frozen=True)
class Usage:
    """What the provider reported for one call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hit_tokens: int = 0
    cost_usd: float = 0.0
    requests: int = 1

    @property
    def tokens(self) -> int:
        return max(0, self.prompt_tokens) + max(0, self.completion_tokens)


@dataclass(frozen=True)
class Reservation:
    estimate: Estimate
    day: str
    month: str

    @property
    def amount_usd(self) -> float:
        return self.estimate.usd


def daily_bucket(moment: datetime | None = None) -> str:
    return (moment or utcnow()).strftime("%Y%m%d")


def monthly_bucket(moment: datetime | None = None) -> str:
    return (moment or utcnow()).strftime("%Y%m")


def period_for(moment: datetime, *, windows: str, days: str, holidays: str = "") -> str:
    from news_api.platform.offpeak import is_peak

    return "peak" if is_peak(moment, windows=windows, days=days, holidays=holidays) else "off_peak"


def _rates(pricing: dict[str, Any], period: str) -> tuple[float, float, float]:
    """(cache-hit, cache-miss, output) USD per million tokens for the period."""
    if period == "off_peak":
        return (
            float(pricing.get("cache_hit_offpeak_price_per_million", 0.003)),
            float(pricing.get("input_offpeak_price_per_million", 0.15)),
            float(pricing.get("output_offpeak_price_per_million", 0.60)),
        )
    return (
        float(pricing.get("cache_hit_price_per_million", 0.006)),
        float(pricing.get("input_price_per_million", 0.30)),
        float(pricing.get("output_price_per_million", 1.20)),
    )


def _cache_hit_tokens(usage: dict[str, Any]) -> int:
    hit = usage.get("prompt_cache_hit_tokens")
    if hit is None:
        details = usage.get("prompt_tokens_details")
        if isinstance(details, dict):
            hit = details.get("cached_tokens")
    try:
        return max(0, int(hit or 0))
    except (TypeError, ValueError):
        return 0


def usage_from_response(usage: dict[str, Any], *, period: str) -> Usage:
    """Provider-reported usage, cache hits priced as hits."""
    prompt = max(0, int(usage.get("prompt_tokens") or 0))
    completion = max(0, int(usage.get("completion_tokens") or 0))
    hit = min(prompt, _cache_hit_tokens(usage))
    return Usage(
        prompt_tokens=prompt,
        completion_tokens=completion,
        cache_hit_tokens=hit,
        cost_usd=usage_cost(usage, period=period),
    )


def usage_cost(usage: dict[str, Any], *, period: str) -> float:
    """Local cost of one call, cache hits priced as hits.

    ``prompt_tokens`` is the sum of hit and miss tokens; when the split is
    absent every prompt token is priced as a miss, which is the conservative
    reading, never zero.
    """
    pricing = scoring_config().get("ai", {})
    hit_rate, miss_rate, output_rate = _rates(pricing, period)
    prompt = max(0, int(usage.get("prompt_tokens") or 0))
    completion = max(0, int(usage.get("completion_tokens") or 0))
    hit = min(prompt, _cache_hit_tokens(usage))
    miss = prompt - hit
    return (hit * hit_rate + miss * miss_rate + completion * output_rate) / 1_000_000


def estimate_tokens(messages: list[dict[str, str]], *, max_tokens: int) -> int:
    characters = sum(len(str(message.get("content") or "")) for message in messages)
    prompt_tokens = max(1, math.ceil(characters / _CHARS_PER_TOKEN))
    return prompt_tokens + max(0, int(max_tokens))


def estimate_cost(
    messages: list[dict[str, str]],
    *,
    max_tokens: int,
    safety: float = _SAFETY,
) -> float:
    """Worst case in USD for the reservation: peak rates, full output."""
    pricing = scoring_config().get("ai", {})
    _, miss_rate, output_rate = _rates(pricing, "peak")
    characters = sum(len(str(message.get("content") or "")) for message in messages)
    prompt_tokens = max(1, math.ceil(characters / _CHARS_PER_TOKEN))
    return ((prompt_tokens * miss_rate) + (max_tokens * output_rate)) / 1_000_000 * safety


def estimate(messages: list[dict[str, str]], *, max_tokens: int) -> Estimate:
    return Estimate(
        tokens=estimate_tokens(messages, max_tokens=max_tokens),
        usd=estimate_cost(messages, max_tokens=max_tokens),
    )


def plan_cost(period: str = "off_peak") -> float:
    """What one item summary is expected to cost, for sizing only."""
    pricing = scoring_config().get("ai", {})
    _, miss_rate, output_rate = _rates(pricing, period)
    return (
        (_PLANNING_PROMPT_TOKENS * miss_rate) + (_PLANNING_OUTPUT_TOKENS * output_rate)
    ) / 1_000_000


def plan_tokens() -> int:
    """What one item summary is expected to use, for sizing a run's allowance."""
    return _PLANNING_PROMPT_TOKENS + _PLANNING_OUTPUT_TOKENS


def runs_left_in_period(interval_minutes: int) -> int:
    """How many refreshes this channel still gets before the bucket resets."""
    now = utcnow()
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (first + timedelta(days=32)).replace(day=1)
    seconds_left = max(0.0, (next_month - now).total_seconds())
    per_interval = max(60, int(interval_minutes) * 60)
    return max(1, math.ceil(seconds_left / per_interval))


def runs_left_today(interval_minutes: int) -> int:
    """How many refreshes this channel still gets before the day bucket resets."""
    now = utcnow()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_left = max(0.0, (tomorrow - now).total_seconds())
    per_interval = max(60, int(interval_minutes) * 60)
    return max(1, math.ceil(seconds_left / per_interval))


def allowance(
    *,
    remaining: float,
    runs_left: int,
    item_cost: float,
    maximum: int,
) -> int:
    """Items this run may attempt.

    Spend what is left across the runs still due, keeping a fifth back for desk
    briefs, featured picks and offer drafts. Dimension-agnostic: pass dollars
    and a dollar-per-item estimate, or tokens and a token-per-item estimate.
    """
    if remaining <= 0 or item_cost <= 0 or maximum <= 0:
        return 0
    share = remaining * 0.8 / max(1, runs_left)
    return max(0, min(int(maximum), int(share / item_cost)))


async def _read_rows(session: Any, day: str, month: str) -> list[dict[str, Any]]:
    result = await session.execute(
        text(
            """
            SELECT bucket_kind, bucket, requests, requests_held,
                   tokens_prompt + tokens_completion AS tokens, tokens_held,
                   cost_usd, cost_held_usd, halted_reason, halted_until
            FROM ai_usage
            WHERE (bucket_kind, bucket) IN (('day', :day), ('month', :month))
            ORDER BY bucket_kind
            FOR UPDATE
            """
        ),
        {"day": day, "month": month},
    )
    return [dict(row) for row in result.mappings().all()]


async def _ensure_rows(session: Any, day: str, month: str) -> None:
    await session.execute(
        text(
            """
            INSERT INTO ai_usage (bucket_kind, bucket)
            VALUES ('day', :day), ('month', :month)
            ON CONFLICT ON CONSTRAINT ai_usage_pk DO NOTHING
            """
        ),
        {"day": day, "month": month},
    )


def _halted(row: dict[str, Any], now: datetime) -> str | None:
    reason = row.get("halted_reason")
    if not reason:
        return None
    until = row.get("halted_until")
    if until is not None and until <= now:
        return None
    return str(reason)


async def reserve(est: Estimate, limits: Limits) -> Reservation:
    """Book the worst case in both buckets, or deny the call.

    Denial reasons: the period is halted, a cap would be crossed, or the
    ledger cannot be read. All three raise :class:`BudgetExceeded` except the
    last, which raises :class:`BudgetUnavailable` - the caller turns both into
    "do not call the provider".
    """
    day, month = daily_bucket(), monthly_bucket()
    now = utcnow()
    try:
        async with session_scope() as session:
            await _ensure_rows(session, day, month)
            rows = await _read_rows(session, day, month)
            for row in rows:
                reason = _halted(row, now)
                if reason:
                    raise BudgetExceeded(f"ai halted: {reason}", reason=f"halted:{reason}")
            for row in rows:
                max_requests, max_tokens, max_usd = limits.for_bucket(str(row["bucket_kind"]))
                used_requests = int(row["requests"]) + int(row["requests_held"])
                used_tokens = int(row["tokens"]) + int(row["tokens_held"])
                used_usd = float(row["cost_usd"]) + float(row["cost_held_usd"])
                bucket = f"{row['bucket_kind']} {row['bucket']}"
                if used_requests + 1 > max_requests:
                    raise BudgetExceeded(f"ai request cap reached for {bucket}", reason="requests")
                if used_tokens + est.tokens > max_tokens:
                    raise BudgetExceeded(f"ai token cap reached for {bucket}", reason="tokens")
                if used_usd + est.usd > max_usd + _EPSILON:
                    raise BudgetExceeded(f"ai budget reached for {bucket}", reason="usd")
            await session.execute(
                text(
                    """
                    UPDATE ai_usage
                    SET requests_held = requests_held + 1,
                        tokens_held = tokens_held + :tokens,
                        cost_held_usd = cost_held_usd + :usd,
                        updated_at = now()
                    WHERE (bucket_kind, bucket) IN (('day', :day), ('month', :month))
                    """
                ),
                {"tokens": est.tokens, "usd": est.usd, "day": day, "month": month},
            )
    except (BudgetExceeded, BudgetUnavailable):
        raise
    except Exception as exc:  # ledger unreachable -> do not spend blind
        raise BudgetUnavailable(type(exc).__name__) from exc
    return Reservation(estimate=est, day=day, month=month)


async def _book(reservation: Reservation, usage: Usage) -> None:
    """Release the hold and book ``usage`` into both buckets."""
    try:
        async with session_scope() as session:
            await _ensure_rows(session, reservation.day, reservation.month)
            await session.execute(
                text(
                    """
                    UPDATE ai_usage
                    SET requests_held = GREATEST(requests_held - 1, 0),
                        tokens_held = GREATEST(tokens_held - :held_tokens, 0),
                        cost_held_usd = GREATEST(cost_held_usd - :held_usd, 0),
                        requests = requests + :requests,
                        tokens_prompt = tokens_prompt + :prompt,
                        tokens_completion = tokens_completion + :completion,
                        tokens_cache_hit = tokens_cache_hit + :cache_hit,
                        cost_usd = cost_usd + :cost,
                        updated_at = now()
                    WHERE (bucket_kind, bucket) IN (('day', :day), ('month', :month))
                    """
                ),
                {
                    "held_tokens": reservation.estimate.tokens,
                    "held_usd": reservation.estimate.usd,
                    "requests": usage.requests,
                    "prompt": usage.prompt_tokens,
                    "completion": usage.completion_tokens,
                    "cache_hit": usage.cache_hit_tokens,
                    "cost": max(0.0, usage.cost_usd),
                    "day": reservation.day,
                    "month": reservation.month,
                },
            )
    except Exception as exc:
        # The call already happened. Losing the booking under-counts the ledger,
        # which is the unsafe direction, so it is loud rather than silent.
        log.error("ai.ledger_settle_failed", error=type(exc).__name__)


async def settle(reservation: Reservation, usage: Usage) -> Usage:
    """Release the hold and book the provider's reported usage."""
    await _book(reservation, usage)
    return usage


async def settle_worst_case(reservation: Reservation) -> Usage:
    """The request left and the outcome is unknown: book the reservation.

    A timeout or an unparsable 200 may still have been billed, so the ledger
    assumes it was. Tokens are booked as prompt tokens because the split is
    unknown; the dollar figure is the reserved worst case.
    """
    usage = Usage(
        prompt_tokens=reservation.estimate.tokens,
        completion_tokens=0,
        cache_hit_tokens=0,
        cost_usd=reservation.estimate.usd,
    )
    await _book(reservation, usage)
    return usage


async def release(reservation: Reservation) -> None:
    """The provider refused the call: book the request, not the money.

    A 4xx still reached the provider, so it counts against the request caps -
    that is what bounds a storm of rejected calls - but it was not billed, so
    no tokens and no dollars are booked.
    """
    await _book(reservation, Usage(requests=1))


async def halt(reason: str, *, for_seconds: int | None = None) -> None:
    """Stop every later call in both buckets until resumed (or until expiry)."""
    day, month = daily_bucket(), monthly_bucket()
    until = utcnow() + timedelta(seconds=for_seconds) if for_seconds else None
    try:
        async with session_scope() as session:
            await _ensure_rows(session, day, month)
            await session.execute(
                text(
                    """
                    UPDATE ai_usage
                    SET halted_reason = :reason, halted_until = :until, updated_at = now()
                    WHERE (bucket_kind, bucket) IN (('day', :day), ('month', :month))
                    """
                ),
                {"reason": reason[:80], "until": until, "day": day, "month": month},
            )
    except Exception as exc:  # pragma: no cover - ledger failure while halting
        log.error("ai.halt_failed", error=type(exc).__name__, reason=reason)
        raise BudgetUnavailable(type(exc).__name__) from exc
    log.warning("ai.halted", reason=reason, until=until.isoformat() if until else None)


async def mark_exhausted() -> None:
    """The provider said 402: stop calling until an operator resumes."""
    await halt("provider_402")


async def resume(*, by: str | None = None) -> None:
    """Clear a halt. Only an operator action calls this."""
    day, month = daily_bucket(), monthly_bucket()
    async with session_scope() as session:
        await _ensure_rows(session, day, month)
        await session.execute(
            text(
                """
                UPDATE ai_usage
                SET halted_reason = NULL, halted_until = NULL, updated_at = now()
                WHERE (bucket_kind, bucket) IN (('day', :day), ('month', :month))
                """
            ),
            {"day": day, "month": month},
        )
    log.info("ai.resumed", by=by or "operator")


async def snapshot(limits: Limits) -> dict[str, Any]:
    """Read-only view for the admin panel, metrics and an operator's sanity check.

    A ledger this stack cannot read raises :class:`BudgetUnavailable`: the
    caller decides whether that is "unavailable" (admin read) or "deny"
    (reserve path).
    """
    day, month = daily_bucket(), monthly_bucket()
    now = utcnow()
    try:
        async with session_scope() as session:
            rows = await _read_rows(session, day, month)
    except Exception as exc:
        raise BudgetUnavailable(type(exc).__name__) from exc
    by_kind = {str(row["bucket_kind"]): row for row in rows}
    halted_reason: str | None = None
    halted_until: datetime | None = None
    for row in rows:
        reason = _halted(row, now)
        if reason:
            halted_reason = reason
            halted_until = row.get("halted_until")
    buckets: dict[str, Any] = {}
    for kind, bucket in (("day", day), ("month", month)):
        # A bucket with no row yet is a bucket with nothing spent: the panel
        # shows the caps and zeros rather than a hole before the first call.
        row = by_kind.get(kind, {})
        max_requests, max_tokens, max_usd = limits.for_bucket(kind)
        requests = int(row.get("requests") or 0)
        tokens = int(row.get("tokens") or 0)
        cost = float(row.get("cost_usd") or 0.0)
        held_requests = int(row.get("requests_held") or 0)
        held_tokens = int(row.get("tokens_held") or 0)
        held_usd = float(row.get("cost_held_usd") or 0.0)
        buckets[kind] = {
            "bucket": bucket,
            "requests": requests,
            "tokens": tokens,
            "cost_usd": round(cost, 6),
            "held_requests": held_requests,
            "held_tokens": held_tokens,
            "held_usd": round(held_usd, 6),
            "limits": {
                "requests": max_requests,
                "tokens": max_tokens,
                "usd": max_usd,
            },
            "remaining": {
                "requests": max(0, max_requests - requests - held_requests),
                "tokens": max(0, max_tokens - tokens - held_tokens),
                "usd": round(max(0.0, max_usd - cost - held_usd), 6),
            },
        }
    return {
        "day": buckets["day"],
        "month": buckets["month"],
        "halted_reason": halted_reason,
        "halted_until": halted_until.isoformat() if halted_until else None,
    }


async def remaining_tokens(limits: Limits) -> int:
    """Tokens still promiseable in whichever bucket is tighter."""
    try:
        state = await snapshot(limits)
    except BudgetUnavailable:
        return 0
    leftovers = [
        bucket["remaining"]["tokens"] for bucket in (state.get("day"), state.get("month")) if bucket
    ]
    return min(leftovers) if leftovers else 0
