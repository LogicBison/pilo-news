"""The limit ledger against real Postgres: it must hold the line, not approximate it.

Every cap is asserted on the dimension an operator would notice - dollars,
tokens and requests, per day and per month - because a ceiling denominated only
in dollars is only as true as the price table behind it.
"""

import pytest

from news_api.articles.infrastructure import ai_budget
from news_api.articles.infrastructure.ai_budget import Estimate, Limits, Usage

ROOMY = Limits(
    daily_tokens=1_000_000,
    monthly_tokens=10_000_000,
    daily_requests=10_000,
    monthly_requests=100_000,
    daily_usd=10.0,
    monthly_usd=100.0,
)


def limits(**over: object) -> Limits:
    values = {
        "daily_tokens": 1_000_000,
        "monthly_tokens": 10_000_000,
        "daily_requests": 10_000,
        "monthly_requests": 100_000,
        "daily_usd": 10.0,
        "monthly_usd": 100.0,
    }
    values.update(over)
    return Limits(**values)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_reserve_then_settle_books_the_real_usage(clean_db) -> None:
    reservation = await ai_budget.reserve(Estimate(tokens=1_000, usd=0.10), ROOMY)
    state = await ai_budget.snapshot(ROOMY)
    # The hold already counts against both buckets.
    assert state["month"]["remaining"]["usd"] == pytest.approx(99.90, abs=1e-6)
    assert state["day"]["held_tokens"] == 1_000

    await ai_budget.settle(
        reservation,
        Usage(prompt_tokens=600, completion_tokens=120, cache_hit_tokens=400, cost_usd=0.0002),
    )
    state = await ai_budget.snapshot(ROOMY)
    assert state["month"]["cost_usd"] == pytest.approx(0.0002, abs=1e-9)
    assert state["month"]["tokens"] == 720
    assert state["month"]["requests"] == 1
    assert state["month"]["held_tokens"] == 0
    assert state["month"]["remaining"]["usd"] == pytest.approx(99.9998, abs=1e-6)


@pytest.mark.asyncio
async def test_two_reservations_cannot_share_the_same_money(clean_db) -> None:
    tight = limits(daily_usd=1.0, monthly_usd=1.0)
    await ai_budget.reserve(Estimate(tokens=100, usd=0.60), tight)
    with pytest.raises(ai_budget.BudgetExceeded) as exc:
        await ai_budget.reserve(Estimate(tokens=100, usd=0.60), tight)
    assert exc.value.reason == "usd"


@pytest.mark.asyncio
async def test_the_ceiling_is_exact(clean_db) -> None:
    tight = limits(daily_usd=1.0, monthly_usd=1.0)
    await ai_budget.reserve(Estimate(tokens=100, usd=1.0), tight)
    with pytest.raises(ai_budget.BudgetExceeded):
        await ai_budget.reserve(Estimate(tokens=1, usd=0.000001), tight)


@pytest.mark.asyncio
async def test_the_token_cap_holds_even_when_the_price_table_is_wrong(clean_db) -> None:
    """A dollar cap trusts `scoring.json`; a token cap does not (finding D9)."""
    token_bound = limits(daily_tokens=1_000, monthly_tokens=1_000)
    await ai_budget.reserve(Estimate(tokens=900, usd=0.000001), token_bound)
    with pytest.raises(ai_budget.BudgetExceeded) as exc:
        await ai_budget.reserve(Estimate(tokens=900, usd=0.000001), token_bound)
    assert exc.value.reason == "tokens"


@pytest.mark.asyncio
async def test_the_request_cap_bounds_a_run_of_free_calls(clean_db) -> None:
    """Requests are what the provider rate-limits and what its console counts."""
    request_bound = limits(daily_requests=2, monthly_requests=2)
    for _ in range(2):
        reservation = await ai_budget.reserve(Estimate(tokens=1, usd=0.0), request_bound)
        await ai_budget.release(reservation)
    with pytest.raises(ai_budget.BudgetExceeded) as exc:
        await ai_budget.reserve(Estimate(tokens=1, usd=0.0), request_bound)
    assert exc.value.reason == "requests"


@pytest.mark.asyncio
async def test_the_daily_bucket_binds_before_the_monthly_one(clean_db) -> None:
    daily = limits(daily_tokens=500, monthly_tokens=100_000)
    await ai_budget.settle(
        await ai_budget.reserve(Estimate(tokens=500, usd=0.0), daily),
        Usage(prompt_tokens=500, cost_usd=0.0),
    )
    with pytest.raises(ai_budget.BudgetExceeded) as exc:
        await ai_budget.reserve(Estimate(tokens=1, usd=0.0), daily)
    assert "day" in str(exc.value)


@pytest.mark.asyncio
async def test_the_ledger_survives_a_redis_flush(clean_db) -> None:
    """Finding D8: the cap used to live only in Redis, so a lost volume reset it."""
    from news_api.platform.cache import get_redis

    await ai_budget.settle(
        await ai_budget.reserve(Estimate(tokens=100, usd=0.5), ROOMY),
        Usage(prompt_tokens=100, cost_usd=0.5),
    )
    client = await get_redis()
    await client.flushdb()

    state = await ai_budget.snapshot(ROOMY)
    assert state["month"]["cost_usd"] == pytest.approx(0.5, abs=1e-9)
    assert state["month"]["tokens"] == 100


@pytest.mark.asyncio
async def test_a_halt_stops_every_later_call_until_an_operator_resumes(clean_db) -> None:
    await ai_budget.halt("auth_401")
    with pytest.raises(ai_budget.BudgetExceeded) as exc:
        await ai_budget.reserve(Estimate(tokens=1, usd=0.0), ROOMY)
    assert exc.value.reason == "halted:auth_401"

    await ai_budget.resume(by="operator")
    reservation = await ai_budget.reserve(Estimate(tokens=1, usd=0.0), ROOMY)
    assert reservation.estimate.tokens == 1


@pytest.mark.asyncio
async def test_a_402_stops_the_period(clean_db) -> None:
    await ai_budget.mark_exhausted()
    with pytest.raises(ai_budget.BudgetExceeded):
        await ai_budget.reserve(Estimate(tokens=1, usd=0.0), ROOMY)


@pytest.mark.asyncio
async def test_a_breaker_halt_expires_by_itself(clean_db) -> None:
    await ai_budget.halt("circuit_breaker", for_seconds=-1)
    # Already expired: the next call is allowed without an operator.
    await ai_budget.reserve(Estimate(tokens=1, usd=0.0), ROOMY)


@pytest.mark.asyncio
async def test_an_unreadable_ledger_denies_the_call(monkeypatch, clean_db) -> None:
    def broken(*_args, **_kwargs):
        raise RuntimeError("database down")

    monkeypatch.setattr(ai_budget, "session_scope", broken)
    with pytest.raises(ai_budget.BudgetUnavailable):
        await ai_budget.reserve(Estimate(tokens=1, usd=0.0), ROOMY)
    with pytest.raises(ai_budget.BudgetUnavailable):
        await ai_budget.snapshot(ROOMY)
    assert await ai_budget.remaining_tokens(ROOMY) == 0


@pytest.mark.asyncio
async def test_settling_more_than_reserved_never_goes_negative(clean_db) -> None:
    reservation = await ai_budget.reserve(Estimate(tokens=10, usd=0.001), ROOMY)
    await ai_budget.settle(reservation, Usage(prompt_tokens=5_000, cost_usd=0.05))
    state = await ai_budget.snapshot(ROOMY)
    assert state["month"]["cost_usd"] == pytest.approx(0.05, abs=1e-9)
    assert state["month"]["held_usd"] == pytest.approx(0.0, abs=1e-9)
    assert state["month"]["held_tokens"] == 0


@pytest.mark.asyncio
async def test_an_unknown_outcome_books_the_worst_case(clean_db) -> None:
    reservation = await ai_budget.reserve(Estimate(tokens=800, usd=0.25), ROOMY)
    await ai_budget.settle_worst_case(reservation)
    state = await ai_budget.snapshot(ROOMY)
    assert state["month"]["cost_usd"] == pytest.approx(0.25, abs=1e-9)
    assert state["month"]["tokens"] == 800
    assert state["month"]["requests"] == 1


@pytest.mark.asyncio
async def test_an_unusable_200_books_the_hold_instead_of_leaking_it(monkeypatch, clean_db) -> None:
    """A 200 that cannot be parsed was still sent: book it, do not strand a hold."""
    import httpx

    from news_api.articles.infrastructure import ai_client as module
    from news_api.platform.settings import get_settings

    monkeypatch.setenv("AI_ENABLED", "true")
    monkeypatch.setenv("AI_API_KEY", "test-key")
    monkeypatch.setenv("AI_OFFPEAK_ONLY", "false")
    get_settings.cache_clear()

    def handler(_request):
        return httpx.Response(200, json={"choices": []})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        ai = module.AIClient(client=client)
        # Two attempts, both unusable: summarize gives up without raising.
        assert await ai.summarize(title="Title", excerpt="Excerpt", language="en") is None
    finally:
        await client.aclose()
        get_settings.cache_clear()

    state = await ai_budget.snapshot(ROOMY)
    assert state["month"]["held_usd"] == pytest.approx(0.0, abs=1e-9)
    assert state["month"]["cost_usd"] > 0


@pytest.mark.asyncio
async def test_a_rejected_key_halts_the_stack_instead_of_retrying(monkeypatch, clean_db) -> None:
    """Finding D2: a 401 booked nothing and was retried for every candidate."""
    import httpx

    from news_api.articles.infrastructure import ai_client as module
    from news_api.platform.settings import get_settings

    monkeypatch.setenv("AI_ENABLED", "true")
    monkeypatch.setenv("AI_API_KEY", "revoked-key")
    monkeypatch.setenv("AI_OFFPEAK_ONLY", "false")
    get_settings.cache_clear()
    sent = {"count": 0}

    def handler(_request):
        sent["count"] += 1
        return httpx.Response(401, json={"error": "invalid key"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        ai = module.AIClient(client=client)
        assert await ai.summarize(title="Title", excerpt="Excerpt", language="en") is None
        # The halt is in the ledger, so a *new* client is stopped too, and it is
        # stopped before the request is sent.
        fresh = module.AIClient(client=client)
        assert await fresh.summarize(title="Other", excerpt="Excerpt", language="en") is None
    finally:
        await client.aclose()
        get_settings.cache_clear()

    assert sent["count"] == 1
    state = await ai_budget.snapshot(ROOMY)
    assert state["halted_reason"] == "auth_401"
    # The rejected request still reached the provider, so it is counted - that
    # is what bounds a storm of them - but it was not billed.
    assert state["month"]["requests"] == 1
    assert state["month"]["tokens"] == 0
    assert state["month"]["cost_usd"] == pytest.approx(0.0, abs=1e-9)


@pytest.mark.asyncio
async def test_a_halted_ledger_gives_a_run_no_items(clean_db) -> None:
    """A halted stack sizes the run at zero instead of walking the candidate pool."""
    from news_api.articles.infrastructure import ai_client as module

    await ai_budget.halt("auth_401")
    assert await module.AIClient().allowance(interval_minutes=720, desks=5) == 0

    await ai_budget.resume(by="test")
    assert await module.AIClient().allowance(interval_minutes=720, desks=5) > 0
