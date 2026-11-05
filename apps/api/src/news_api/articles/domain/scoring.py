from __future__ import annotations

from datetime import datetime
from typing import Any

from news_api.articles.domain.models import Candidate, Topic
from news_api.platform.clock import utcnow
from news_api.platform.config import scoring_config


def _title_bonus(title: str, config: dict[str, Any]) -> float:
    length = len(title)
    rules = config.get("title_length_bonus", {})
    ideal_min = int(rules.get("ideal_min", 30))
    ideal_max = int(rules.get("ideal_max", 120))
    if ideal_min <= length <= ideal_max:
        return float(rules.get("ideal", 0.35))
    return float(rules.get("short", 0.1))


def _recency(published_at: datetime, now: datetime, config: dict[str, Any]) -> float:
    hours = max(0.0, (now - published_at).total_seconds() / 3600)
    rules = config.get("recency", {})
    half_life = float(rules.get("half_life_hours", 72)) or 72.0
    floor = float(rules.get("floor", 0.15))
    return max(floor, 0.5 ** (hours / half_life))


def match_topics(candidate: Candidate, topics: list[Topic]) -> list[Topic]:
    haystack = f"{candidate.title} {candidate.excerpt}".casefold()
    matched: list[Topic] = []
    for topic in topics:
        if candidate.seed_topics and topic.slug in candidate.seed_topics:
            matched.append(topic)
            continue
        if any(
            keyword and keyword in haystack for keyword in topic.keywords_for(candidate.language)
        ):
            matched.append(topic)
    if candidate.seed_topics:
        by_slug = {topic.slug: topic for topic in topics}
        for slug in candidate.seed_topics:
            seed_topic = by_slug.get(slug)
            if seed_topic and seed_topic not in matched:
                matched.append(seed_topic)
    return matched


def score_candidate(
    candidate: Candidate,
    topics: list[Topic],
    *,
    now: datetime | None = None,
    config: dict[str, Any] | None = None,
) -> Candidate | None:
    rules = config or scoring_config()
    moment = now or utcnow()
    matched = match_topics(candidate, topics)

    require_topic = bool(rules.get("require_topic_match", True))
    if not matched and require_topic and not candidate.pinned:
        return None

    keyword_weight = float(rules.get("keyword_weight", 1.0))
    trust_weight = float(rules.get("trust_weight", 2.0))
    topic_multiplier = min(1.3, 1.0 + 0.1 * max(0, len(matched) - 1))
    topic_weight = max((topic.weight for topic in matched), default=1.0)

    base = (
        keyword_weight * topic_multiplier * topic_weight
        + trust_weight * candidate.source_trust
        + _title_bonus(candidate.title, rules)
    )
    score = base * _recency(candidate.published_at, moment, rules)
    if candidate.pinned:
        score += float(rules.get("pin_bonus", 5.0))

    if score < float(rules.get("min_score", 0.35)) and not candidate.pinned:
        return None

    candidate.score = round(score, 4)
    candidate.topics = matched
    return candidate


def score_pool(
    candidates: list[Candidate],
    topics: list[Topic],
    *,
    now: datetime | None = None,
    config: dict[str, Any] | None = None,
) -> list[Candidate]:
    rules = config or scoring_config()
    scored = [score_candidate(item, topics, now=now, config=rules) for item in candidates]
    return [item for item in scored if item is not None]
