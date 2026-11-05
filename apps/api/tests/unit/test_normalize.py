from datetime import UTC, datetime

import pytest

from news_api.articles.infrastructure.normalize import (
    article_uuid,
    canonicalize_url,
    clean_text,
    parse_feed,
    repair_mojibake,
)

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Example News</title>
<item><title>Court &amp; regulator update</title>
<link>https://www.example.com/story/?utm_source=feed&amp;id=7#top</link>
<description>&lt;p&gt;A &lt;b&gt;compliance&lt;/b&gt; change.&lt;/p&gt;</description>
<pubDate>Wed, 05 Nov 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Atom Desk</title>
<entry><title>Bank capital rules</title><link rel="alternate" href="https://news.example.org/bank-rules"/>
<updated>2026-11-05T09:00:00Z</updated><summary>Banks must revise capital plans.</summary></entry></feed>"""


def test_clean_text_strips_html_and_entities() -> None:
    assert clean_text("<p>Hello &amp;amp; goodbye</p>") == "Hello & goodbye"


def test_clean_text_unwraps_escaped_cdata_markers() -> None:
    assert clean_text("&lt;![CDATA[Our Continued Evolution]]&gt;") == "Our Continued Evolution"


def test_repair_mojibake() -> None:
    broken = "RegulaciÃ³n financiera"
    assert repair_mojibake(broken) == "Regulación financiera"


def test_canonicalize_tracking_and_case() -> None:
    url = canonicalize_url("HTTPS://WWW.Example.COM/Path/?utm_source=x&id=3&fbclid=y#frag")
    assert url == "https://example.com/Path?id=3"


def test_canonicalize_rejects_non_http() -> None:
    assert canonicalize_url("javascript:alert(1)") == ""


def test_article_uuid_is_stable() -> None:
    first = article_uuid("source", "https://example.com/a", "Title")
    second = article_uuid("source", "https://example.com/a", "Title")
    assert first == second
    assert first != article_uuid("source", "https://example.com/a", "Other")


def test_parse_rss() -> None:
    items = parse_feed(RSS, source_name="Example", language="en")
    assert len(items) == 1
    assert items[0].title == "Court & regulator update"
    assert items[0].link == "https://example.com/story?id=7"
    assert items[0].excerpt == "A compliance change."
    assert items[0].published_at == datetime(2026, 11, 5, 10, 0, tzinfo=UTC)


def test_parse_atom() -> None:
    items = parse_feed(ATOM, source_name="Atom", language="en")
    assert len(items) == 1
    assert items[0].publisher == "Atom Desk"
    assert items[0].link == "https://news.example.org/bank-rules"


def test_email_publisher_falls_back_to_outlet_name() -> None:
    feed = b"""<?xml version="1.0"?><rss version="2.0"><channel>
    <title>The Hacker News</title>
    <item><title>Story</title><link>https://example.com/a</link>
    <source>info@thehackernes.com (The Hacker News)</source></item>
    </channel></rss>"""
    items = parse_feed(feed, source_name="THN", language="en")
    assert items[0].publisher == "The Hacker News"


def test_parse_feed_rejects_entities() -> None:
    with pytest.raises(ValueError):
        parse_feed(b'<!DOCTYPE x [<!ENTITY y "z">]><rss/>', source_name="x", language="en")


def test_parse_feed_skips_unusable_entries() -> None:
    payload = b"<rss><channel><item><description>no title</description></item></channel></rss>"
    assert parse_feed(payload, source_name="x", language="en") == []
