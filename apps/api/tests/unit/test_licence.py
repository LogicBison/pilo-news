"""Licence-aware ingestion: a proprietary source is headline and link only."""

from types import SimpleNamespace

from news_api.articles.application.ingest import _feed_candidates
from news_api.articles.domain.models import FeedItem
from news_api.articles.infrastructure.normalize import parse_datetime

RSS = b"""<rss><channel><title>Desk</title>
<item><title>Regulator opens consultation</title>
<link>https://example.com/story</link>
<description>The regulator opened a consultation on fees.</description>
<pubDate>Wed, 05 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>"""


def _source(licence: str) -> SimpleNamespace:
    return SimpleNamespace(
        id="00000000-0000-0000-0000-000000000001",
        name="Paid Wire",
        trust=0.9,
        language="en",
        licence_type=licence,
    )


def _outcome() -> SimpleNamespace:
    item = FeedItem(
        title="Regulator opens consultation",
        link="https://example.com/story",
        published_at=parse_datetime("Wed, 05 Nov 2026 10:00:00 GMT"),
        excerpt="The regulator opened a consultation on fees.",
        publisher="Paid Wire",
    )
    return SimpleNamespace(items=[item])


def test_proprietary_source_keeps_only_the_headline_and_link() -> None:
    [candidate] = _feed_candidates(_source("proprietary"), _outcome(), "ind", [])
    assert candidate.headline_only is True
    assert candidate.excerpt == ""
    assert candidate.title == "Regulator opens consultation"
    assert candidate.canonical_url.startswith("https://example.com/")


def test_public_domain_source_keeps_the_excerpt() -> None:
    [candidate] = _feed_candidates(_source("public-domain"), _outcome(), "ind", [])
    assert candidate.headline_only is False
    assert candidate.excerpt.startswith("The regulator")
