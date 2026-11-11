"""Global AI budget: reserve -> call -> settle, fail closed.

The previous rule checked ``spent >= budget`` once before a call. Three holes
made that a suggestion rather than a ceiling: a concurrent worker or a retry
could slip past the check, a client timeout discarded the usage of a call the
provider had already billed, and an unreachable Redis made ``get_float``
return ``0.0`` — silently switching the cap off.

This module reserves the **worst case** (peak rates, full ``max_tokens``)
before the request and settles the provider-reported usage after it. If the
ledger cannot be read or written, the call is denied: the desk keeps serving,
it just stops paying. A 402 from the provider marks the period exhausted so
the rest of the process does not keep trying.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog

from news_api.platform.cache import get_redis
from news_api.platform.clock import monthly_bucket, utcnow
from news_api.platform.config import scoring_config

log = structlog.get_logger(__name__)

RESERVE_SCRIPT = """
if redis.call('EXISTS', KEYS[3]) == 1 then
  return -1
end
local spent = tonumber(redis.call('GET', KEYS[1]) or '0')
local held = tonumber(redis.call('GET', KEYS[2]) or '0')
local add = tonumber(ARGV[1])
local cap = tonumber(ARGV[2])
if spent + held + add > cap + 0.000000001 then
  return 0
end
redis.call('INCRBYFLOAT', KEYS[2], ARGV[1])
redis.call('EXPIREAT', KEYS[1], ARGV[3])
redis.call('EXPIREAT', KEYS[2], ARGV[3])
return 1
"""

SETTLE_SCRIPT = """
local held = tonumber(redis.call('GET', KEYS[2]) or '0')
local reserved = tonumber(ARGV[1])
local actual = tonumber(ARGV[2])
local next_held = held - reserved
if next_held < 0 then
  next_held = 0
end
redis.call('SET', KEYS[2], string.format('%.12f', next_held))
local spent = redis.call('INCRBYFLOAT', KEYS[1], ARGV[2])
redis.call('EXPIREAT', KEYS[1], ARGV[3])
redis.call('EXPIREAT', KEYS[2], ARGV[3])
return spent
"""

# Used only to size a run's allowance, never for accounting.
_PLANNING_PROMPT_TOKENS = 400
_PLANNING_OUTPUT_TOKENS = 160


class BudgetExceeded(Exception):
    """The ceiling would be crossed, or the provider already answered 402."""


class BudgetUnavailable(Exception):
    """The ledger cannot be trusted right now, so no money is spent."""


@dataclass(frozen=True)
class Reservation:
    amount_usd: float
    budget_usd: float

    @property
    def key(self) -> str:
        return _spend_key()


def _spend_key() -> str:
    return f"ai:spend:{monthly_bucket()}"


def _held_key() -> str:
    return f"ai:held:{monthly_bucket()}"


def _exhausted_key() -> str:
    return f"ai:exhausted:{monthly_bucket()}"


def _expire_at() -> int:
    now = utcnow()
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (first + timedelta(days=32)).replace(day=1)
    # Keep the bucket readable for a few days after the period ends so a late
    # reconciliation or a human reading the key still finds it.
    return int((next_month + timedelta(days=5)).timestamp())


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


def estimate_cost(
    messages: list[dict[str, str]],
    *,
    max_tokens: int,
    safety: float = 1.05,
) -> float:
    """Worst case for the reservation: peak rates, full output.

    Tokenizers differ; three characters per token with a 5% margin is a
    deliberately pessimistic count. Over-reserving only delays the next call —
    it never lets one through.
    """
    pricing = scoring_config().get("ai", {})
    _, miss_rate, output_rate = _rates(pricing, "peak")
    characters = sum(len(str(message.get("content") or "")) for message in messages)
    prompt_tokens = max(1, math.ceil(characters / 3))
    return ((prompt_tokens * miss_rate) + (max_tokens * output_rate)) / 1_000_000 * safety


def plan_cost(period: str = "off_peak") -> float:
    """What one item summary is expected to cost, for sizing only."""
    pricing = scoring_config().get("ai", {})
    _, miss_rate, output_rate = _rates(pricing, period)
    return (
        (_PLANNING_PROMPT_TOKENS * miss_rate) + (_PLANNING_OUTPUT_TOKENS * output_rate)
    ) / 1_000_000


def runs_left_in_period(interval_minutes: int) -> int:
    """How many refreshes this channel still gets before the bucket resets."""
    now = utcnow()
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (first + timedelta(days=32)).replace(day=1)
    seconds_left = max(0.0, (next_month - now).total_seconds())
    per_interval = max(60, int(interval_minutes) * 60)
    return max(1, math.ceil(seconds_left / per_interval))


def allowance(
    *,
    remaining_usd: float,
    runs_left: int,
    item_cost_usd: float,
    maximum: int,
) -> int:
    """Items this run may summarise.

    Spend the rest of the ceiling across the runs still due, keeping a fifth
    back for desk briefs and featured picks. At $1 the first day affords a
    handful per run, not sixty: the cap is the point.
    """
    if remaining_usd <= 0 or item_cost_usd <= 0 or maximum <= 0:
        return 0
    share = remaining_usd * 0.8 / max(1, runs_left)
    return max(0, min(int(maximum), int(share / item_cost_usd)))


async def reserve(amount_usd: float, budget_usd: float) -> Reservation:
    if amount_usd <= 0:
        return Reservation(0.0, budget_usd)
    try:
        client = await get_redis()
        result = await client.eval(
            RESERVE_SCRIPT,
            3,
            _spend_key(),
            _held_key(),
            _exhausted_key(),
            f"{amount_usd:.12f}",
            f"{budget_usd:.12f}",
            str(_expire_at()),
        )
    except Exception as exc:  # ledger unreachable -> do not spend blind
        raise BudgetUnavailable(type(exc).__name__) from exc
    code = int(result)
    if code == -1:
        raise BudgetExceeded("provider balance exhausted for this period")
    if code == 0:
        raise BudgetExceeded("ai budget would be exceeded")
    return Reservation(amount_usd, budget_usd)


async def settle(reservation: Reservation, actual_usd: float) -> float:
    """Release the hold, book the real cost, return the period total."""
    try:
        client = await get_redis()
        spent = await client.eval(
            SETTLE_SCRIPT,
            2,
            _spend_key(),
            _held_key(),
            f"{reservation.amount_usd:.12f}",
            f"{max(0.0, actual_usd):.12f}",
            str(_expire_at()),
        )
        return float(spent or 0.0)
    except Exception as exc:  # pragma: no cover - ledger failure after the call
        log.warning("ai.budget_settle_failed", error=type(exc).__name__)
        return 0.0


async def release(reservation: Reservation) -> float:
    return await settle(reservation, 0.0)


async def mark_exhausted() -> None:
    """The provider said 402; stop calling until the bucket resets."""
    try:
        client = await get_redis()
        ttl = max(60, _expire_at() - int(utcnow().timestamp()))
        await client.set(_exhausted_key(), "1", ex=ttl)
    except Exception as exc:  # pragma: no cover
        log.warning("ai.budget_exhausted_flag_failed", error=type(exc).__name__)


async def spent_and_held() -> tuple[float, float]:
    try:
        client = await get_redis()
        values = await client.mget(_spend_key(), _held_key())
    except Exception as exc:
        raise BudgetUnavailable(type(exc).__name__) from exc
    spent = float(values[0] or 0.0) if values else 0.0
    held = float(values[1] or 0.0) if values else 0.0
    return spent, held


async def remaining(budget_usd: float) -> float:
    """What is left to promise. Unknown ledger means zero, never infinity."""
    try:
        spent, held = await spent_and_held()
    except BudgetUnavailable:
        return 0.0
    return max(0.0, float(budget_usd) - spent - held)


async def snapshot() -> dict[str, float | str]:
    """Read-only view for logs, metrics and an operator's sanity check."""
    spent, held = await spent_and_held()
    return {"spent_usd": spent, "held_usd": held, "bucket": monthly_bucket()}


def utc_moment() -> datetime:
    return utcnow().astimezone(UTC)
