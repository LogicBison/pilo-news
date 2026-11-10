"""Discovery: candidate parsing, title normalisation and overlap scoring.

The network path is exercised by `./bin/sources.sh discover` against real feeds;
these tests pin the pure rules that decide what the report means.
"""

from news_api.sources.application.discover import (
    normalize_title,
    overlap_ratio,
    parse_candidates,
    similarity,
    title_tokens,
)

OPML = """<?xml version="1.0"?>
<opml version="2.0"><head><title>feeds</title></head><body>
  <outline text="Desk" title="Desk">
    <outline type="rss" text="A" xmlUrl="https://a.example.com/feed.xml"/>
    <outline type="rss" text="B" xmlUrl="https://b.example.com/feed.xml"/>
    <outline type="rss" text="A again" xmlUrl="https://a.example.com/feed.xml"/>
  </outline>
</body></opml>"""


def test_parse_candidates_handles_a_plain_list() -> None:
    text = "# comment\nhttps://a.example.com/feed.xml\n\nhttps://b.example.com/feed.xml\n"
    assert parse_candidates(text) == [
        "https://a.example.com/feed.xml",
        "https://b.example.com/feed.xml",
    ]


def test_parse_candidates_reads_opml_and_dedupes() -> None:
    assert parse_candidates(OPML) == [
        "https://a.example.com/feed.xml",
        "https://b.example.com/feed.xml",
    ]


def test_normalize_title_drops_punctuation_and_case() -> None:
    assert normalize_title("EU adopts the AI Act — finally!") == "eu adopts the ai act finally"


def test_overlap_counts_only_titles_the_desk_already_has() -> None:
    existing = [title_tokens("Regulator fines three banks")]
    titles = ["Regulator fines three banks", "A brand new story"]
    assert overlap_ratio(titles, existing) == 0.5
    assert overlap_ratio([], existing) == 0.0


def test_overlap_recognises_a_reworded_headline() -> None:
    existing = [title_tokens("Regulator fines three banks")]
    assert (
        similarity(
            title_tokens("Three banks fined by regulator"),
            existing[0],
        )
        >= 0.6
    )
    assert overlap_ratio(["Three banks fined by regulator"], existing) == 1.0
    assert similarity(title_tokens("Bank results"), existing[0]) < 0.6


def test_opml_export_round_trips_through_discovery() -> None:
    from news_api.sources.application.portfolio import to_opml

    rows = [
        {
            "industry": "legal",
            "name": "A",
            "feed_url": "https://a.example.com/feed.xml",
            "language": "en",
        },
        {
            "industry": "legal",
            "name": "B",
            "feed_url": "https://b.example.com/feed.xml",
            "language": "es",
        },
        {
            "industry": "financial",
            "name": "C",
            "feed_url": "https://c.example.com/feed.xml",
            "language": "en",
        },
    ]
    document = to_opml(rows)
    assert 'xmlUrl="https://a.example.com/feed.xml"' in document
    # The export is valid OPML that discovery can read back (grouped by desk,
    # so the order is by industry, not by input order).
    assert set(parse_candidates(document)) == {row["feed_url"] for row in rows}
