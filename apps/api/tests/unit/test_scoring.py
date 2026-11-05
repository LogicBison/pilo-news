from datetime import timedelta

from news_api.articles.domain.models import Candidate, Topic
from news_api.articles.domain.scoring import match_topics, score_candidate
from news_api.platform.clock import utcnow

TOPICS = [
    Topic(
        id="t1",
        slug="regulation",
        weight=1.4,
        keywords={"en": ["regulator", "compliance"], "es": ["regulador", "cumplimiento"]},
        label={"en": "Regulation", "es": "Regulación"},
    ),
    Topic(
        id="t2",
        slug="markets",
        weight=1.1,
        keywords={"en": ["market", "stocks"], "es": ["mercado", "bolsa"]},
        label={"en": "Markets", "es": "Mercados"},
    ),
]


def candidate(**overrides):
    values = {
        "industry_id": "00000000-0000-0000-0000-000000000001",
        "source_id": None,
        "source_name": "Source",
        "source_trust": 0.9,
        "title": "Regulator issues compliance guidance for banks",
        "url": "https://example.com/a",
        "canonical_url": "https://example.com/a",
        "excerpt": "The regulator published new compliance guidance.",
        "publisher": "Publisher",
        "language": "en",
        "published_at": utcnow() - timedelta(hours=1),
    }
    values.update(overrides)
    return Candidate(**values)


def test_match_topics_uses_language_keywords() -> None:
    matched = match_topics(candidate(), TOPICS)
    assert [topic.slug for topic in matched] == ["regulation"]


def test_score_candidate_excludes_unmatched_by_default() -> None:
    result = score_candidate(candidate(title="Sports results", excerpt="A game"), TOPICS)
    assert result is None


def test_pinned_candidate_survives_topic_requirement() -> None:
    result = score_candidate(
        candidate(title="Sports results", excerpt="A game", pinned=True), TOPICS
    )
    assert result is not None
    assert result.score >= 5.0


def test_recency_reduces_score() -> None:
    fresh = score_candidate(candidate(), TOPICS)
    old = score_candidate(candidate(published_at=utcnow() - timedelta(days=20)), TOPICS)
    assert fresh is not None and old is not None
    assert fresh.score > old.score


def test_spanish_keywords_match() -> None:
    result = score_candidate(
        candidate(
            language="es",
            title="El regulador publica guía de cumplimiento",
            excerpt="La nueva guía de cumplimiento afecta a los bancos.",
        ),
        TOPICS,
    )
    assert result is not None
    assert result.topics[0].slug == "regulation"
