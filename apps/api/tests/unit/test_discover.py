"""Discovery: candidate parsing, title normalisation and overlap scoring.

The network path is exercised by `./bin/sources.sh discover` against real feeds;
these tests pin the pure rules that decide what the report means.
"""

from news_api.sources.application.discover import (
    normalize_title,
    overlap_ratio,
    parse_candidates,
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
    existing = {normalize_title("Regulator fines three banks")}
    titles = ["Regulator fines three banks", "A brand new story"]
    assert overlap_ratio(titles, existing) == 0.5
    assert overlap_ratio([], existing) == 0.0
