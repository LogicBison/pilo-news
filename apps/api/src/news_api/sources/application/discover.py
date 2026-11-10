"""Discovery: would this feed earn a place on a desk?

The question is not "does it parse" — `verify-sources` answers that for feeds we
already trust. A candidate has to pass four independent tests:

1. **Permission** — robots.txt must allow the feed path (checked first, so a
   refused host is never contacted).
2. **Quality** — the same policy `verify-sources` applies: item count, freshness,
   language, duplicate titles.
3. **Novelty** — how much of it we already carry. A feed that repeats the desk
   is more work, not more coverage.
4. **Fit** — it must not already be configured anywhere.

Read-only: discovery prints a report and a profile snippet. Adding a source
stays an explicit profile edit, because a profile is the reviewable record.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit
from xml.etree import ElementTree

from news_api.articles.infrastructure import repo as articles_repo
from news_api.articles.infrastructure.fetcher import fetch_source
from news_api.articles.infrastructure.politeness import HostLedger, robots_snapshot
from news_api.channels.infrastructure import repo as channels_repo
from news_api.sources.application.quality import assess_feed, detect_language
from news_api.sources.domain.models import Source
from news_api.sources.domain.validation import normalize_feed_url, validate_feed_url
from news_api.sources.infrastructure import repo as sources_repo

#: Tolerable share of a candidate's items already carried by the desk. Above
#: this the feed adds noise: a fourth wire on the same 20 stories.
MAX_OVERLAP = 0.5
#: Trust a candidate starts at; it must still clear the policy floor of 0.75.
SUGGESTED_TRUST = 0.8

TITLE_NOISE_RE = re.compile(r"[^a-z0-9]+")
#: Two headlines count as the same story above this token overlap. Exact match
#: is 1.0; a reworded headline usually lands near 0.6-0.8.
SIMILARITY_THRESHOLD = 0.6


def normalize_title(title: str) -> str:
    return TITLE_NOISE_RE.sub(" ", title.casefold()).strip()


def parse_candidates(text: str) -> list[str]:
    """URLs from a plain list or an OPML export.

    OPML is what feed readers export, and it is the practical way an operator
    hands over twenty candidates at once.
    """
    text = text.strip()
    if not text:
        return []
    if "<opml" in text[:400].lower():
        return _parse_opml(text)
    urls: list[str] = []
    for line in text.splitlines():
        candidate = line.split(",")[0].strip()
        if not candidate or candidate.startswith("#"):
            continue
        urls.append(candidate)
    return _dedupe(urls)


def _parse_opml(text: str) -> list[str]:
    root = ElementTree.fromstring(text)
    urls = [
        node.attrib["xmlUrl"].strip() for node in root.iter("outline") if node.attrib.get("xmlUrl")
    ]
    return _dedupe(urls)


def _dedupe(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for url in urls:
        key = normalize_feed_url(url)
        if key not in seen:
            seen.add(key)
            out.append(url)
    return out


def title_tokens(title: str) -> frozenset[str]:
    return frozenset(normalize_title(title).split())


def similarity(left: frozenset[str], right: frozenset[str]) -> float:
    """Token overlap, tolerant of a reworded headline.

    Jaccard alone under-counts a paraphrase ("regulator fines three banks" vs
    "three banks fined by regulator"); the overlap coefficient catches it. The
    max of the two is the usual near-duplicate compromise and is explainable
    to a reviewer.
    """
    if not left or not right:
        return 0.0
    shared = len(left & right)
    if not shared:
        return 0.0
    jaccard = shared / len(left | right)
    containment = shared / min(len(left), len(right))
    return max(jaccard, containment)


def overlap_ratio(
    titles: list[str],
    existing: list[frozenset[str]],
    *,
    threshold: float = SIMILARITY_THRESHOLD,
) -> float:
    """Share of titles the desk already carries, allowing reworded headlines."""
    if not titles:
        return 0.0
    hits = 0
    for title in titles:
        tokens = title_tokens(title)
        if any(similarity(tokens, other) >= threshold for other in existing):
            hits += 1
    return round(hits / len(titles), 3)


def _probe_source(url: str, language: str) -> Source:
    return Source(
        id="00000000-0000-0000-0000-000000000000",
        industry_id="00000000-0000-0000-0000-000000000000",
        name=urlsplit(url).hostname or url,
        feed_url=url,
        language=language,
        trust=SUGGESTED_TRUST,
        enabled=True,
        allow_http=False,
        poll_interval_min=720,
        terms_checked_at=None,
        terms_url=None,
        etag=None,
        last_modified=None,
        last_fetched_at=None,
        last_success_at=None,
        status="active",
        consecutive_failures=0,
        last_error=None,
    )


@dataclass
class Candidate:
    url: str
    verdict: str
    reasons: list[str]
    grade: str | None = None
    items: int = 0
    language: str | None = None
    language_confidence: float = 0.0
    newest_item_days: float | None = None
    overlap: float = 0.0
    robots_allowed: bool | None = None
    crawl_delay: int | None = None
    duplicate_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


async def discover(
    candidates: list[str],
    *,
    industry: str | None = None,
    limit: int = 40,
    save: bool = False,
) -> dict[str, Any]:
    """Grade each candidate against permission, quality, novelty and fit."""
    industry_id: str | None = None
    if industry:
        channel = await channels_repo.get_channel(industry, enabled_only=False)
        if not channel:
            raise ValueError(f"unknown industry: {industry}")
        industry_id = channel.id

    existing_sources = await sources_repo.list_sources(include_disabled=True)
    configured = {normalize_feed_url(item.feed_url): item for item in existing_sources}
    recent = await articles_repo.recent_titles(industry_id)
    existing_titles = [title_tokens(title) for title in recent if title]

    rows: list[Candidate] = []
    for url in candidates[:limit]:
        rows.append(
            await _evaluate(
                url,
                configured=configured,
                existing_titles=existing_titles,
                industry_id=industry_id,
            )
        )

    accepted = [row for row in rows if row.verdict == "accept"]
    saved = 0
    if save:
        saved = await sources_repo.upsert_candidates(
            [
                {
                    "feed_url": row.url,
                    "name": urlsplit(row.url).hostname or row.url,
                    "industry_id": industry_id,
                    "language": row.language or "",
                    "grade": row.grade,
                    "overlap": row.overlap,
                    "verdict": row.verdict,
                }
                for row in rows
                if row.verdict != "reject" or row.duplicate_of is None
            ]
        )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "industry": industry,
        "candidates": [row.to_dict() for row in rows],
        "summary": {
            "candidates": len(rows),
            "accept": len(accepted),
            "review": sum(1 for row in rows if row.verdict == "review"),
            "reject": sum(1 for row in rows if row.verdict == "reject"),
            "saved": saved,
        },
        "profile_snippet": [
            {
                "name": urlsplit(row.url).hostname or row.url,
                "feed_url": row.url,
                "language": row.language or "en",
                "trust": SUGGESTED_TRUST,
                "enabled": True,
                "allow_http": False,
                "poll_interval_min": 720,
                "terms_url": None,
                "licence_type": "unknown",
            }
            for row in accepted
        ],
    }


async def _overlap(
    titles: list[str],
    existing_titles: list[frozenset[str]],
    industry_id: str | None,
) -> float:
    """pg_trgm first (the database's near-duplicate measure), token match if the
    extension is not available."""
    try:
        return await articles_repo.overlap_share(titles, industry_id)
    except Exception:  # extension missing or query error: stay useful
        return overlap_ratio(titles, existing_titles)


async def _evaluate(
    url: str,
    *,
    configured: dict[str, Source],
    existing_titles: list[frozenset[str]],
    industry_id: str | None = None,
) -> Candidate:
    key = normalize_feed_url(url)
    duplicate = configured.get(key)
    if duplicate is not None:
        state = "enabled" if duplicate.enabled else "disabled"
        return Candidate(
            url=url,
            verdict="reject",
            reasons=[f"already configured ({state}): {duplicate.name}"],
            duplicate_of=duplicate.name,
        )

    problems = validate_feed_url(url, allow_http=False)
    if problems:
        return Candidate(url=url, verdict="reject", reasons=problems)

    allowed, crawl_delay, _digest = await robots_snapshot(url)
    if not allowed:
        return Candidate(
            url=url,
            verdict="reject",
            reasons=["robots.txt disallows this path"],
            robots_allowed=False,
            crawl_delay=int(crawl_delay) if crawl_delay else None,
        )

    outcome = await fetch_source(
        _probe_source(url, "en"),
        check_robots=False,
        ledger=HostLedger(mode="off"),
    )
    if outcome.status != "ok":
        return Candidate(
            url=url,
            verdict="reject",
            reasons=[f"fetch failed: {outcome.status}"],
            robots_allowed=True,
        )

    titles = [item.title for item in outcome.items]
    detected, confidence = detect_language(titles)
    report = assess_feed(
        source_name=urlsplit(url).hostname or url,
        declared_language=detected or "en",
        trust=SUGGESTED_TRUST,
        status=outcome.status,
        items=list(outcome.items),
    )
    metrics = report.metrics
    overlap = await _overlap(titles, existing_titles, industry_id)

    reasons = list(report.issues)
    if overlap > MAX_OVERLAP:
        reasons.append(f"overlap {overlap:.0%}: the desk already carries these stories")

    verdict = "accept"
    if not report.passed:
        verdict = "reject"
    elif overlap > MAX_OVERLAP or report.grade not in ("A", "B"):
        verdict = "review"

    return Candidate(
        url=url,
        verdict=verdict,
        reasons=reasons,
        grade=report.grade,
        items=int(metrics.get("items") or 0),
        language=detected or None,
        language_confidence=float(metrics.get("language_confidence") or 0.0),
        newest_item_days=metrics.get("newest_item_days"),
        overlap=overlap,
        robots_allowed=True,
        crawl_delay=int(crawl_delay) if crawl_delay else None,
    )


async def refresh_candidates(*, older_than_days: int = 7, limit: int = 10) -> dict[str, Any]:
    """Re-grade queued candidates that have been sitting for a while.

    Status is never touched: a shortlisted feed stays shortlisted even if its
    grade moved. Only the numbers behind the decision are refreshed, so a stale
    queue cannot be approved on last month's evidence.
    """
    rows = await sources_repo.stale_candidates(older_than_days, limit=limit)
    existing_sources = await sources_repo.list_sources(include_disabled=True)
    configured = {normalize_feed_url(item.feed_url): item for item in existing_sources}
    recent = await articles_repo.recent_titles(None)
    existing = [title_tokens(title) for title in recent if title]

    updated: list[dict[str, Any]] = []
    for row in rows:
        industry_id = str(row["industry_id"]) if row.get("industry_id") else None
        candidate = await _evaluate(
            str(row["feed_url"]),
            configured=configured,
            existing_titles=existing,
            industry_id=industry_id,
        )
        await sources_repo.update_candidate_metrics(
            str(row["id"]),
            grade=candidate.grade,
            overlap=candidate.overlap,
            verdict=candidate.verdict,
            language=candidate.language or "",
        )
        updated.append(
            {
                "id": str(row["id"]),
                "feed_url": candidate.url,
                "verdict": candidate.verdict,
                "grade": candidate.grade,
                "overlap": candidate.overlap,
                "reasons": candidate.reasons,
            }
        )
    return {"checked": len(rows), "candidates": updated}
