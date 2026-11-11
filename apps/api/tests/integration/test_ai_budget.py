"""The budget ledger against a real Redis: it must hold the line, not approximate it."""

import pytest

from news_api.articles.infrastructure import ai_budget


@pytest.mark.asyncio
async def test_reserve_then_settle_books_the_real_cost(clean_db) -> None:
    reservation = await ai_budget.reserve(0.10, 1.0)
    assert reservation.amount_usd == pytest.approx(0.10)
    # The hold already counts against the ceiling.
    assert await ai_budget.remaining(1.0) == pytest.approx(0.90, abs=1e-6)

    spent = await ai_budget.settle(reservation, 0.0002)
    assert spent == pytest.approx(0.0002, abs=1e-9)
    assert await ai_budget.remaining(1.0) == pytest.approx(0.9998, abs=1e-6)


@pytest.mark.asyncio
async def test_two_reservations_cannot_share_the_same_money(clean_db) -> None:
    await ai_budget.reserve(0.60, 1.0)
    with pytest.raises(ai_budget.BudgetExceeded):
        await ai_budget.reserve(0.60, 1.0)


@pytest.mark.asyncio
async def test_the_ceiling_is_exact(clean_db) -> None:
    await ai_budget.reserve(1.0, 1.0)
    with pytest.raises(ai_budget.BudgetExceeded):
        await ai_budget.reserve(0.000001, 1.0)


@pytest.mark.asyncio
async def test_a_402_flag_stops_every_later_call(clean_db) -> None:
    await ai_budget.mark_exhausted()
    with pytest.raises(ai_budget.BudgetExceeded):
        await ai_budget.reserve(0.001, 1.0)


@pytest.mark.asyncio
async def test_an_unreadable_ledger_denies_the_call(monkeypatch, clean_db) -> None:
    async def broken():
        raise RuntimeError("redis down")

    monkeypatch.setattr(ai_budget, "get_redis", broken)
    with pytest.raises(ai_budget.BudgetUnavailable):
        await ai_budget.reserve(0.001, 1.0)
    assert await ai_budget.remaining(1.0) == 0.0


@pytest.mark.asyncio
async def test_settling_more_than_reserved_never_goes_negative(clean_db) -> None:
    reservation = await ai_budget.reserve(0.001, 1.0)
    await ai_budget.settle(reservation, 0.05)
    spent, held = await ai_budget.spent_and_held()
    assert spent == pytest.approx(0.05, abs=1e-9)
    assert held == pytest.approx(0.0, abs=1e-9)


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

    spent, held = await ai_budget.spent_and_held()
    assert held == pytest.approx(0.0, abs=1e-9)
    assert spent > 0
