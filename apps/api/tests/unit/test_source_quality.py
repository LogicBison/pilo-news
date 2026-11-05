"""Unit tests for the source quality policy."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from news_api.articles.domain.models import FeedItem
from news_api.sources.application.quality import (
    MIN_SOURCES_PER_INDUSTRY,
    assess_feed,
    coverage_warnings,
    detect_language,
)

NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)


def item(title: str, days_old: int = 1) -> FeedItem:
    return FeedItem(
        title=title,
        link=f"https://example.org/{abs(hash(title))}",
        published_at=NOW - timedelta(days=days_old),
        excerpt="",
        publisher="Example",
    )


def english_feed(count: int = 12, days_old: int = 1) -> list[FeedItem]:
    return [
        item(f"The market and the policy of the day {index}", days_old) for index in range(count)
    ]


def spanish_feed(count: int = 12, days_old: int = 1) -> list[FeedItem]:
    return [
        item(f"El gobierno y los estados con una nueva ley {index}", days_old)
        for index in range(count)
    ]


def test_detects_spanish_and_english_titles() -> None:
    assert detect_language([entry.title for entry in spanish_feed(6)])[0] == "es"
    assert detect_language([entry.title for entry in english_feed(6)])[0] == "en"


def test_healthy_feed_passes_with_top_grade() -> None:
    report = assess_feed(
        source_name="Healthy",
        declared_language="en",
        trust=0.9,
        status="ok",
        items=english_feed(),
        now=NOW,
    )
    assert report.passed is True
    assert report.grade == "A"
    assert report.issues == []


def test_thin_feed_fails() -> None:
    report = assess_feed(
        source_name="Thin",
        declared_language="en",
        trust=0.9,
        status="ok",
        items=english_feed(count=2),
        now=NOW,
    )
    assert report.passed is False
    assert any("at least" in issue for issue in report.issues)


def test_stale_feed_fails() -> None:
    report = assess_feed(
        source_name="Stale",
        declared_language="en",
        trust=0.9,
        status="ok",
        items=english_feed(days_old=60),
        now=NOW,
    )
    assert report.passed is False
    assert any("stale" in issue for issue in report.issues)


def test_language_mismatch_fails() -> None:
    report = assess_feed(
        source_name="Mismatch",
        declared_language="en",
        trust=0.9,
        status="ok",
        items=spanish_feed(),
        now=NOW,
    )
    assert report.passed is False
    assert any("language mismatch" in issue for issue in report.issues)


def test_low_trust_is_penalised_but_not_fatal() -> None:
    report = assess_feed(
        source_name="LowTrust",
        declared_language="en",
        trust=0.6,
        status="ok",
        items=english_feed(),
        now=NOW,
    )
    assert report.passed is True
    assert report.grade == "B"
    assert any("trust" in issue for issue in report.issues)


def test_fetch_failure_scores_zero() -> None:
    report = assess_feed(
        source_name="Down",
        declared_language="en",
        trust=0.9,
        status="http_error",
        items=[],
        now=NOW,
    )
    assert report.score == 0.0
    assert report.passed is False


def test_coverage_policy_flags_thin_and_single_language_channels() -> None:
    warnings = coverage_warnings(languages=["en"], enabled_sources=2, trust_values=[0.9, 0.6])
    assert any(str(MIN_SOURCES_PER_INDUSTRY) in warning for warning in warnings)
    assert any("no es source" in warning for warning in warnings)
    assert any("trust" in warning for warning in warnings)

    assert coverage_warnings(languages=["en", "es"], enabled_sources=4, trust_values=[0.9]) == []
