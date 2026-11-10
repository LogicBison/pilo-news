"""Source value and retirement proposals: crude, explainable rules."""

from news_api.sources.application.value import retirement_reason, value_score


def test_clicks_weigh_more_than_items() -> None:
    assert value_score(10, 0) == 10.0
    assert value_score(10, 2) == 20.0


def test_a_source_with_no_items_from_attempts_is_proposed() -> None:
    row = {
        "enabled": True,
        "attempts_30d": 5,
        "items_30d": 0,
        "clicks_30d": 0,
        "success_rate_30d": 0.2,
    }
    assert retirement_reason(row) == "no items from 5 attempts"


def test_a_thin_source_with_no_clicks_is_proposed() -> None:
    row = {
        "enabled": True,
        "attempts_30d": 20,
        "items_30d": 3,
        "clicks_30d": 0,
        "success_rate_30d": 0.9,
    }
    assert retirement_reason(row) == "thin (3 items) with no return clicks"


def test_a_thin_source_that_sends_readers_is_left_alone() -> None:
    row = {
        "enabled": True,
        "attempts_30d": 20,
        "items_30d": 3,
        "clicks_30d": 7,
        "success_rate_30d": 0.9,
    }
    assert retirement_reason(row) is None


def test_a_disabled_source_is_never_proposed() -> None:
    row = {
        "enabled": False,
        "attempts_30d": 5,
        "items_30d": 0,
        "clicks_30d": 0,
        "success_rate_30d": 0.0,
    }
    assert retirement_reason(row) is None
