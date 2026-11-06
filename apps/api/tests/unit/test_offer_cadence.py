from __future__ import annotations

from datetime import date

from news_api.offers.domain.cadence import latest_due_date


def test_weekly_due_date_is_the_latest_weekday() -> None:
    wednesday = {"kind": "weekly", "weekday": 2}
    assert latest_due_date(wednesday, date(2026, 11, 6)) == date(2026, 11, 4)
    assert latest_due_date(wednesday, date(2026, 11, 4)) == date(2026, 11, 4)
    assert latest_due_date(wednesday, date(2026, 11, 9)) == date(2026, 11, 4)


def test_monthly_nth_weekday_due_date() -> None:
    first_tuesday = {"kind": "monthly", "weekday": 1, "nth": 1}
    assert latest_due_date(first_tuesday, date(2026, 11, 6)) == date(2026, 11, 3)
    assert latest_due_date(first_tuesday, date(2026, 11, 3)) == date(2026, 11, 3)
    before = latest_due_date(first_tuesday, date(2026, 10, 1))
    assert before is not None
    assert before.month == 9
    assert before < date(2026, 10, 1)


def test_monthly_day_and_invalid_cadence() -> None:
    assert latest_due_date({"kind": "monthly", "day": 15}, date(2026, 11, 6)) == date(2026, 10, 15)
    assert latest_due_date({"kind": "monthly", "day": 5}, date(2026, 11, 6)) == date(2026, 11, 5)
    assert latest_due_date({"kind": "weekly", "weekday": 9}, date(2026, 11, 6)) is None
    assert latest_due_date({"kind": "nope"}, date(2026, 11, 6)) is None
