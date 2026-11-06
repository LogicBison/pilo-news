from __future__ import annotations

from news_api.channels.domain.offers import (
    default_offers,
    merge_offers,
    resolve_offers,
    validate_offers,
)


def test_defaults_preserve_the_one_secondary_rung() -> None:
    plain = default_offers({})
    assert plain == {"consultation": True, "brief": True, "question": True, "asset": False}

    with_asset = default_offers({"asset": "legal-regulatory-calendar"})
    assert with_asset == {
        "consultation": True,
        "brief": False,
        "question": True,
        "asset": True,
    }


def test_explicit_switches_override_defaults() -> None:
    resolved = resolve_offers(
        {"asset": "legal-regulatory-calendar"},
        {"consultation": False, "brief": True, "asset": False},
    )
    assert resolved == {
        "consultation": False,
        "brief": True,
        "question": True,
        "asset": False,
    }


def test_an_unconfigured_channel_gets_all_four_keys() -> None:
    resolved = resolve_offers({}, None)
    assert set(resolved) == {"consultation", "brief", "question", "asset"}
    assert all(isinstance(value, bool) for value in resolved.values())


def test_merge_writes_all_four_keys_from_a_partial_patch() -> None:
    merged = merge_offers({"asset": "kev-digest"}, {}, {"question": False})
    assert merged == {
        "consultation": True,
        "brief": False,
        "question": False,
        "asset": True,
    }


def test_validation_rejects_both_secondary_offers() -> None:
    problems = validate_offers(
        {"asset": "kev-digest"},
        {"consultation": True, "brief": True, "question": True, "asset": True},
    )
    assert any("brief and asset" in problem for problem in problems)


def test_validation_rejects_asset_without_a_slug() -> None:
    problems = validate_offers(
        {},
        {"consultation": True, "brief": False, "question": True, "asset": True},
    )
    assert any("cta.asset" in problem for problem in problems)


def test_validation_rejects_unknown_keys_and_non_booleans() -> None:
    problems = validate_offers(
        {},
        {"consultation": True, "brief": True, "question": True, "asset": False, "newsletter": True},
    )
    assert any("unknown offer" in problem for problem in problems)

    # The API model rejects non-booleans before this function runs, but the
    # domain guard still reports them if a caller bypasses the model.
    problems = validate_offers(
        {},
        {"consultation": True, "brief": "yes", "question": True, "asset": False},  # type: ignore[dict-item]
    )
    assert any("must be true or false" in problem for problem in problems)
