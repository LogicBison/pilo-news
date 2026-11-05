"""Source quality policy.

A feed is accepted for a channel when it clears the automated gates in
`assess_feed` and the editorial trust floor. The policy is deliberately small
and testable: freshness, structure, language agreement, trust, and feed size.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from news_api.articles.domain.models import FeedItem

MIN_ITEMS = 3
SIZE_WARN_ITEMS = 200
STALE_DAYS_FAIL = 45
STALE_DAYS_WARN = 14
MIN_TRUST = 0.75
PASS_SCORE = 0.70
MIN_SOURCES_PER_INDUSTRY = 4

ENGLISH_MARKERS = frozenset(
    {
        "the",
        "and",
        "of",
        "to",
        "for",
        "with",
        "that",
        "this",
        "from",
        "are",
        "is",
        "were",
        "been",
        "will",
        "would",
        "has",
        "have",
        "had",
        "by",
        "at",
        "not",
        "but",
        "its",
        "their",
        "they",
        "which",
    }
)
SPANISH_MARKERS = frozenset(
    {
        "del",
        "los",
        "las",
        "que",
        "por",
        "con",
        "para",
        "una",
        "uno",
        "unos",
        "unas",
        "es",
        "son",
        "como",
        "más",
        "pero",
        "sus",
        "sobre",
        "este",
        "esta",
        "estos",
        "ser",
        "está",
        "están",
        "según",
        "tras",
        "ante",
        "desde",
        "hasta",
    }
)


@dataclass(frozen=True)
class QualityReport:
    score: float
    grade: str
    passed: bool
    issues: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 2),
            "grade": self.grade,
            "passed": self.passed,
            "issues": list(self.issues),
            "metrics": dict(self.metrics),
        }


def detect_language(titles: list[str]) -> tuple[str | None, float]:
    """Cheap stopword vote over titles; returns (language, confidence)."""
    english = 0
    spanish = 0
    for title in titles:
        for word in title.casefold().replace("—", " ").split():
            token = word.strip(".,:;!?()[]\"'“”‘’")
            if token in ENGLISH_MARKERS:
                english += 1
            elif token in SPANISH_MARKERS:
                spanish += 1
    total = english + spanish
    if total < 5:
        return None, 0.0
    if english >= spanish * 1.5:
        return "en", english / total
    if spanish >= english * 1.5:
        return "es", spanish / total
    return None, 0.0


def _grade(score: float) -> str:
    if score >= 0.9:
        return "A"
    if score >= 0.8:
        return "B"
    if score >= PASS_SCORE:
        return "C"
    return "D"


def assess_feed(
    *,
    source_name: str,
    declared_language: str,
    trust: float,
    status: str,
    items: list[FeedItem],
    now: datetime | None = None,
) -> QualityReport:
    """Score one fetched feed against the quality policy."""
    moment = now or datetime.now(UTC)
    issues: list[str] = []
    hard_fail = False

    if status not in ("ok", "http_304"):
        return QualityReport(
            score=0.0,
            grade="D",
            passed=False,
            issues=[f"fetch failed: {status}"],
            metrics={"items": 0, "status": status},
        )

    count = len(items)
    metrics: dict[str, Any] = {
        "items": count,
        "status": status,
        "declared_language": declared_language,
        "trust": trust,
    }

    if count < MIN_ITEMS:
        issues.append(f"only {count} item(s); need at least {MIN_ITEMS}")
        hard_fail = True
    elif count < 10:
        issues.append(f"thin feed ({count} items)")

    if count > SIZE_WARN_ITEMS:
        issues.append(f"oversized feed ({count} items); paginate or narrow it")

    newest_days: float | None = None
    if items:
        newest = max(item.published_at for item in items)
        if newest.tzinfo is None:
            newest = newest.replace(tzinfo=UTC)
        newest_days = (moment - newest).total_seconds() / 86400
        metrics["newest_item_days"] = round(newest_days, 1)
        if newest_days > STALE_DAYS_FAIL:
            issues.append(f"stale: newest item is {newest_days:.0f} days old")
            hard_fail = True
        elif newest_days > STALE_DAYS_WARN:
            issues.append(f"aging: newest item is {newest_days:.0f} days old")
        elif newest_days < -3:
            issues.append(f"newest item is dated {-newest_days:.0f} days in the future")

    detected, confidence = detect_language([item.title for item in items])
    metrics["detected_language"] = detected
    metrics["language_confidence"] = round(confidence, 2)
    if detected and confidence >= 0.75 and detected != declared_language:
        issues.append(f"language mismatch: declared {declared_language}, feed looks {detected}")
        hard_fail = True

    if trust < MIN_TRUST:
        issues.append(f"trust {trust:.2f} below floor {MIN_TRUST:.2f}")

    duplicates = len(items) - len({item.title.casefold() for item in items})
    if items and duplicates / len(items) > 0.4:
        issues.append(f"{duplicates} duplicate titles in feed")

    score = 1.0
    score -= 0.5 if count < MIN_ITEMS else 0.0
    score -= 0.1 if 0 < count < 10 else 0.0
    score -= 0.1 if count > SIZE_WARN_ITEMS else 0.0
    if newest_days is not None:
        if newest_days > STALE_DAYS_FAIL:
            score -= 0.4
        elif newest_days > STALE_DAYS_WARN or newest_days < -3:
            score -= 0.1
    if detected and confidence >= 0.75 and detected != declared_language:
        score -= 0.5
    if trust < MIN_TRUST:
        score -= 0.2
    if items and duplicates / len(items) > 0.4:
        score -= 0.1
    score = max(0.0, min(1.0, score))

    return QualityReport(
        score=score,
        grade=_grade(score),
        passed=(not hard_fail) and score >= PASS_SCORE,
        issues=issues,
        metrics=metrics,
    )


def coverage_warnings(
    languages: list[str], enabled_sources: int, trust_values: list[float]
) -> list[str]:
    """Per-channel source coverage policy, evaluated after a profile import."""
    warnings: list[str] = []
    if enabled_sources < MIN_SOURCES_PER_INDUSTRY:
        warnings.append(
            f"only {enabled_sources} enabled source(s); the policy minimum is "
            f"{MIN_SOURCES_PER_INDUSTRY}"
        )
    for language in ("en", "es"):
        if language not in languages:
            warnings.append(f"no {language} source; each supported language needs at least one")
    if trust_values and min(trust_values) < MIN_TRUST:
        warnings.append(f"lowest trust is {min(trust_values):.2f}; floor is {MIN_TRUST:.2f}")
    return warnings
