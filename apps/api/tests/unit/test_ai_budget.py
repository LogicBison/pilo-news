"""Budget arithmetic: it must over-reserve, settle truthfully, and throttle."""

from datetime import UTC, datetime

from pytest import approx

from news_api.articles.infrastructure import ai_budget
from news_api.platform.offpeak import is_peak


def test_cache_hits_are_priced_as_hits() -> None:
    hit_heavy = {
        "prompt_tokens": 10_000,
        "prompt_cache_hit_tokens": 9_000,
        "completion_tokens": 100,
    }
    miss_heavy = {**hit_heavy, "prompt_cache_hit_tokens": 0}
    assert ai_budget.usage_cost(hit_heavy, period="off_peak") < ai_budget.usage_cost(
        miss_heavy, period="off_peak"
    )


def test_a_missing_split_is_priced_as_a_miss_never_zero() -> None:
    without_split = {"prompt_tokens": 10_000, "completion_tokens": 0}
    assert ai_budget.usage_cost(without_split, period="off_peak") > 0


def test_peak_costs_twice_the_off_peak_rate() -> None:
    usage = {"prompt_tokens": 10_000, "prompt_cache_hit_tokens": 0, "completion_tokens": 1_000}
    peak = ai_budget.usage_cost(usage, period="peak")
    cheap = ai_budget.usage_cost(usage, period="off_peak")
    assert peak == approx(cheap * 2, rel=0.001)


def test_the_reservation_is_the_worst_case_at_peak_rates() -> None:
    messages = [{"role": "system", "content": "x" * 3_000}]
    small = ai_budget.estimate_cost(messages, max_tokens=100)
    large = ai_budget.estimate_cost(messages, max_tokens=4_000)
    assert large > small > 0
    # Peak cache-miss input, not the cheaper off-peak rate.
    assert small > (1_000 * 0.30 + 100 * 1.20) / 1_000_000


def test_period_follows_the_published_calendar() -> None:
    assert (
        ai_budget.period_for(
            datetime(2026, 11, 10, 2, 0, tzinfo=UTC),
            windows="01:00-04:00,06:00-10:00",
            days="1,2,3,4,5",
        )
        == "peak"
    )
    assert (
        ai_budget.period_for(
            datetime(2026, 11, 10, 12, 0, tzinfo=UTC),
            windows="01:00-04:00,06:00-10:00",
            days="1,2,3,4,5",
        )
        == "off_peak"
    )


def test_the_peak_calendar_agrees_with_the_helper() -> None:
    moment = datetime(2026, 11, 10, 2, 0, tzinfo=UTC)
    assert is_peak(moment, windows="01:00-04:00", days="1,2,3,4,5") is True


def test_no_money_means_no_items() -> None:
    assert (
        ai_budget.allowance(remaining_usd=0.0, runs_left=10, item_cost_usd=0.00016, maximum=60) == 0
    )


def test_the_allowance_never_exceeds_the_configured_maximum() -> None:
    assert (
        ai_budget.allowance(remaining_usd=100.0, runs_left=1, item_cost_usd=0.0001, maximum=60)
        == 60
    )


def test_a_runs_allowance_never_overcommits_the_remaining_budget() -> None:
    cost = 0.00016
    first_day = ai_budget.allowance(
        remaining_usd=1.0, runs_left=660, item_cost_usd=cost, maximum=60
    )
    late = ai_budget.allowance(remaining_usd=0.05, runs_left=22, item_cost_usd=cost, maximum=60)
    assert 0 < first_day <= 60
    assert first_day * 660 * cost <= 1.0
    assert late * 22 * cost <= 0.05


def test_a_cheap_item_buys_more_than_an_expensive_one() -> None:
    cheap = ai_budget.allowance(remaining_usd=1.0, runs_left=100, item_cost_usd=0.0001, maximum=60)
    dear = ai_budget.allowance(remaining_usd=1.0, runs_left=100, item_cost_usd=0.001, maximum=60)
    assert cheap >= dear


def test_runs_left_is_at_least_one_and_never_zero() -> None:
    assert ai_budget.runs_left_in_period(720) >= 1
    assert ai_budget.runs_left_in_period(5) > ai_budget.runs_left_in_period(1440)
