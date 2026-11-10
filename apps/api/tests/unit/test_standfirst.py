"""D8 (improvement plan): the issue header reads as a sentence, not a row.

``_standfirst`` is the one line above a reference issue's table. The plan asks
for the count and a human date, with no ``Scope:`` prefix (the scope already
renders as its own chip) and no ISO date.
"""

from datetime import date

from news_api.offers.application.build import _pluralise, _standfirst
from news_api.offers.domain.models import OfferDefinition

CHECKED = date(2026, 11, 4)


def make_definition(**overrides) -> OfferDefinition:
    values = {
        "industry": "legal",
        "offer_slug": "legal-regulatory-calendar",
        "name": "US Regulatory Calendar",
        "adapter": "federal_register",
        "scope": "US",
        "cadence": {"kind": "monthly"},
        "lookback_days": 120,
        "max_rows": 12,
        "standfirst_noun": "federal rule change",
    }
    values.update(overrides)
    return OfferDefinition(**values)


def test_counts_the_noun_with_a_human_date() -> None:
    line = _standfirst(make_definition(), CHECKED, 12)
    assert line == "12 federal rule changes, checked 4 November"
    assert "Scope:" not in line
    assert "2026-11-04" not in line  # no ISO date for a reader to decode


def test_singular_keeps_the_config_noun_as_is() -> None:
    assert _standfirst(make_definition(), CHECKED, 1) == "1 federal rule change, checked 4 November"


def test_zero_still_reads_as_english() -> None:
    line = _standfirst(make_definition(), CHECKED, 0)
    assert line == "No federal rule changes in this issue, checked 4 November"


def test_scope_and_chips_are_never_duplicated_here() -> None:
    line = _standfirst(make_definition(scope="US"), CHECKED, 3)
    assert "US" not in line


def test_pluralise_covers_the_config_noun_phrases() -> None:
    assert _pluralise("federal rule change") == "federal rule changes"
    assert _pluralise("newly added vulnerability") == "newly added vulnerabilities"
    assert _pluralise("watch item") == "watch items"
    assert _pluralise("batch") == "batches"
