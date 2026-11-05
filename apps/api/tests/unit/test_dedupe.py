from datetime import timedelta

from news_api.articles.domain.dedupe import dedupe_candidates, title_similarity
from news_api.articles.domain.models import Candidate
from news_api.platform.clock import utcnow


def build(title: str, source: str, score: float, trust: float = 0.9) -> Candidate:
    return Candidate(
        industry_id="00000000-0000-0000-0000-000000000001",
        source_id=None,
        source_name=source,
        source_trust=trust,
        title=title,
        url=f"https://example.com/{source}/{title[:10]}",
        canonical_url=f"https://example.com/{source}/{title[:10]}",
        excerpt="",
        publisher=source,
        language="es",
        published_at=utcnow() - timedelta(hours=1),
        score=score,
    )


def test_unicode_similarity_handles_accents() -> None:
    assert title_similarity("Regulación financiera europea", "Regulación financiera europea") > 0.99
    assert title_similarity("Regulación financiera", "Deportes locales") < 0.4


def test_dedupe_keeps_highest_score_and_counts_sources() -> None:
    items = [
        build("El regulador publica nuevas reglas de capital", "Uno", 2.0),
        build("El regulador publica nuevas reglas de capital", "Dos", 1.8),
        build("Otra noticia completamente distinta sobre puertos", "Tres", 1.5),
    ]
    result = dedupe_candidates(items)
    assert len(result) == 2
    top = result[0]
    assert top.source_name == "Uno"
    assert top.corroboration == 2
    assert top.verification == "corroborated"


def test_single_source_low_trust_is_penalized() -> None:
    item = build("Noticia única sobre un tema distinto", "Blog", 1.0, trust=0.5)
    result = dedupe_candidates([item])
    assert result[0].verification == "single-source"
    assert result[0].score < 1.0
