from datetime import UTC, datetime

import pytest

from news_api.articles.infrastructure.normalize import (
    article_uuid,
    canonicalize_url,
    clean_text,
    parse_feed,
    repair_html_entities,
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


# --- C7: one HTML entity in a publisher's XML must not cost the whole feed ---

HTML_ENTITY_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Inside Higher Ed</title>
<item><title>Heard at a conference</title>
<link>https://www.example.com/story</link>
<description>&lt;p&gt;A new book,&nbsp;&lt;/span&gt; and what follows.&lt;/p&gt;</description>
<pubDate>Mon, 09 Nov 2026 03:00:00 -0500</pubDate></item>
</channel></rss>"""


def test_parse_feed_repairs_html_entities_instead_of_dropping_the_feed() -> None:
    items = parse_feed(HTML_ENTITY_RSS, source_name="Inside Higher Ed", language="en")
    assert len(items) == 1
    assert "book," in items[0].excerpt
    # The non-breaking space becomes the separator it always was.
    assert "\xa0" not in items[0].excerpt


def test_repair_leaves_xml_entities_alone() -> None:
    payload = b"a &amp; b &lt;c&gt; &quot;d&quot; &apos;e&apos; &hellip;&nbsp;end"
    assert (
        repair_html_entities(payload) == b"a &amp; b &lt;c&gt; &quot;d&quot; &apos;e&apos; ... end"
    )


def test_repair_drops_entities_it_cannot_resolve() -> None:
    assert repair_html_entities(b"noise &notathing; end") == b"noise  end"
    # Numeric references are already legal XML: untouched.
    assert repair_html_entities(b"&#169; &#x2014;") == b"&#169; &#x2014;"


def test_repair_keeps_accents_readable() -> None:
    assert repair_html_entities(b"Regulaci&oacute;n") == b"Regulacion"
    assert repair_html_entities(b"caf&eacute; &ndash; open") == b"cafe - open"


# --- C7: a bare ampersand in publisher XML must not cost the feed either ---

BARE_AMP_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Distribucion Actualidad</title>
<item><title>\xc3\x93ptica & Audiolog\xc3\xada Universitaria avanza</title>
<link>https://www.example.com/optica</link>
<description>Un repaso &amp; una nota.</description>
<pubDate>Mon, 09 Nov 2026 03:00:00 -0500</pubDate></item>
</channel></rss>"""


def test_parse_feed_repairs_a_bare_ampersand_in_a_title() -> None:
    items = parse_feed(BARE_AMP_RSS, source_name="Distribucion Actualidad", language="es")
    assert len(items) == 1
    assert items[0].title == "Óptica & Audiología Universitaria avanza"
    assert "&amp;" not in items[0].title


def test_repair_escapes_bare_ampersands_only_outside_cdata() -> None:
    assert repair_html_entities(b"AT&T") == b"AT&amp;T"
    assert repair_html_entities(b"a &amp; b &#38; &#x26;") == b"a &amp; b &#38; &#x26;"
    # Inside CDATA the ampersand is already literal text: escaping it would
    # print "&amp;" to the reader.
    assert repair_html_entities(b"<![CDATA[AT&T]]>") == b"<![CDATA[AT&T]]>"


# --- JSON Feed 1.x ---------------------------------------------------------

JSON_FEED = b"""{
  "version": "https://jsonfeed.org/version/1.1",
  "title": "Example Desk",
  "items": [
    {"id": "1", "url": "https://example.com/a",
     "title": "Regulator opens consultation",
     "summary": "The regulator opened a consultation on fees.",
     "date_published": "2026-11-09T10:00:00Z"},
    {"id": "2", "external_url": "https://example.com/b",
     "title": "Second story", "content_text": "Body text.",
     "date_modified": "2026-11-08T09:00:00Z"}
  ]
}"""


def test_parse_json_feed_maps_the_same_shape() -> None:
    items = parse_feed(JSON_FEED, source_name="fallback", language="en")
    assert [item.title for item in items] == ["Regulator opens consultation", "Second story"]
    assert items[0].link == "https://example.com/a"
    assert items[1].link == "https://example.com/b"
    assert items[0].publisher == "Example Desk"
    assert items[0].published_at.year == 2026


def test_parse_json_feed_rejects_a_json_object_that_is_not_a_feed() -> None:
    with pytest.raises(ValueError):
        parse_feed(b'{"hello": "world"}', source_name="x", language="en")
