from __future__ import annotations

import html
import html.entities
import re
import unicodedata
import uuid
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from xml.etree.ElementTree import ParseError

from defusedxml import ElementTree as DefusedET  # type: ignore[import-untyped]

from news_api.articles.domain.models import FeedItem
from news_api.platform.clock import utcnow

EMAIL_PUBLISHER_RE = re.compile(r"^(?P<email>[^@\s]+@[^@\s]+)\s*(?:\((?P<name>[^)]+)\))?$")

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "ref", "mc_cid", "mc_eid", "igshid", "yclid"}
TAG_RE = re.compile(r"<[^>]+>")
LITERAL_CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
WHITESPACE_RE = re.compile(r"\s+")
MOJIBAKE_MARKERS = ("Ã", "Â", "â€", "Ã©", "Ã³", "Ã±")

# Publishers paste HTML into XML: "&nbsp;" inside a description is not a
# defined XML entity, Expat raises "undefined entity", and one stray character
# would otherwise cost the whole feed (C7: Inside Higher Ed, 4 failures).
HTML_ENTITY_RE = re.compile(
    rb"&(?!#\d+;|#x[0-9a-fA-F]+;|amp;|lt;|gt;|quot;|apos;)[a-zA-Z][a-zA-Z0-9]{1,31};"
)
# A bare "&" is not legal XML either: one publisher puts "Óptica & Audiología"
# straight into a title, and Expat rejects the document (C7: Distribución
# Actualidad, 1 failure). Only the ampersands that do not already open a legal
# reference are escaped.
BARE_AMP_RE = re.compile(rb"&(?!#\d+;|#x[0-9a-fA-F]+;|(?:amp|lt|gt|quot|apos);)")
# CDATA is literal text; escaping an "&" there would print "&amp;" to readers.
CDATA_SPLIT_RE = re.compile(rb"(<!\[CDATA\[.*?\]\]>)", re.DOTALL)
# The five entities XML defines itself: rewriting those would corrupt the text.
XML_PREDEFINED = {"amp;", "lt;", "gt;", "quot;", "apos;"}
# Typography that should survive as readable ASCII rather than disappear.
ASCII_FALLBACK = {
    "\xa0": " ",
    "\u2026": "...",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2022": "-",
    "\u00d7": "x",
}


def repair_html_entities(content: bytes) -> bytes:
    """Replace HTML-only entity references with what a reader would see.

    Output stays ASCII-compatible, so a repaired document keeps whatever
    encoding it declared. An entity we cannot resolve simply disappears — a
    missing ornament beats a dropped feed. A bare ampersand becomes ``&amp;``
    so the document parses and the reader still sees the character.
    """

    def swap(match: re.Match[bytes]) -> bytes:
        name = match.group(0)[1:].decode("ascii", "ignore")
        if name in XML_PREDEFINED:
            return match.group(0)
        char = html.entities.html5.get(name, "")
        if not char:
            return b""
        char = "".join(ASCII_FALLBACK.get(piece, piece) for piece in char)
        return unicodedata.normalize("NFKD", char).encode("ascii", "ignore")

    def repair(chunk: bytes) -> bytes:
        return BARE_AMP_RE.sub(b"&amp;", HTML_ENTITY_RE.sub(swap, chunk))

    return b"".join(
        part if part.startswith(b"<![CDATA[") else repair(part)
        for part in CDATA_SPLIT_RE.split(content)
    )


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"br", "p", "div", "li"}:
            self.parts.append(" ")

    def text(self) -> str:
        return "".join(self.parts)


def strip_html(value: str) -> str:
    if not value:
        return ""
    if "<" in value and ">" in value:
        parser = _TextExtractor()
        try:
            parser.feed(value)
            parser.close()
            value = parser.text()
        except Exception:
            value = TAG_RE.sub(" ", value)
    return value


def repair_mojibake(value: str) -> str:
    if not any(marker in value for marker in MOJIBAKE_MARKERS):
        return value
    try:
        repaired = value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value
    before = sum(value.count(marker) for marker in MOJIBAKE_MARKERS)
    after = sum(repaired.count(marker) for marker in MOJIBAKE_MARKERS)
    return repaired if after < before else value


def clean_text(value: str) -> str:
    if not value:
        return ""
    text = html.unescape(html.unescape(value))
    # Some publishers escape CDATA markers as text instead of using them; unwrap
    # before tag stripping so the title survives.
    text = LITERAL_CDATA_RE.sub(r"\1", text)
    text = strip_html(text)
    text = repair_mojibake(text)
    text = unicodedata.normalize("NFC", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def clean_publisher(value: str, fallback: str) -> str:
    """Reject author emails as publishers; prefer the parenthesised outlet name."""
    text = clean_text(value)
    if not text:
        return fallback
    match = EMAIL_PUBLISHER_RE.match(text)
    if match:
        return clean_text(match.group("name") or "") or fallback
    return text


def canonicalize_url(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    parts = urlsplit(raw)
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https") or not parts.hostname:
        return ""
    host = parts.hostname.lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    port = parts.port
    netloc = host
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{host}:{port}"
    path = parts.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith(TRACKING_PREFIXES) and key.lower() not in TRACKING_KEYS
    ]
    query = urlencode(query_pairs)
    return urlunsplit((scheme, netloc, path, query, ""))


def article_uuid(source_id: str | None, canonical_url: str, title: str) -> str:
    key = f"{source_id or 'seed'}:{canonical_url}|{title.casefold()}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return utcnow()
    text = value.strip()
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return utcnow()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element: object, name: str) -> str:
    for child in list(element):  # type: ignore[call-overload]
        if _local(child.tag) == name:
            return "".join(child.itertext()).strip()
    return ""


def _atom_link(entry: object) -> str:
    fallback = ""
    for child in list(entry):  # type: ignore[call-overload]
        if _local(child.tag) != "link":
            continue
        href = str(child.attrib.get("href") or "").strip()
        if not href:
            continue
        if child.attrib.get("rel") == "canonical":
            return href
        if not fallback:
            fallback = href
    return fallback or _child_text(entry, "link")


def _first_text(entry: object, names: tuple[str, ...]) -> str:
    for name in names:
        value = _child_text(entry, name)
        if value:
            return value
    return ""


def parse_feed(content: bytes, *, source_name: str, language: str) -> list[FeedItem]:
    """Parse RSS 2.0 / Atom safely. Returns normalized candidates (no persistence)."""
    head = content[:4096].lower()
    if b"<!doctype" in head or b"<!entity" in head:
        raise ValueError("DTD/entity declarations are not allowed")
    try:
        root = DefusedET.fromstring(content)
    except ParseError:
        # One HTML entity should not cost the whole feed: repair and retry.
        root = DefusedET.fromstring(repair_html_entities(content))
    root_name = _local(root.tag)
    publisher_default = clean_text(_child_text(root, "title")) if root_name != "feed" else ""
    if root_name == "feed":
        publisher_default = clean_text(_child_text(root, "title")) or source_name

    entries: list[object]
    if root_name == "feed":
        entries = [child for child in list(root) if _local(child.tag) == "entry"]
    elif root_name == "rss":
        entries = []
        for channel in list(root):
            if _local(channel.tag) == "channel":
                entries.extend(child for child in list(channel) if _local(child.tag) == "item")
    else:
        entries = [child for child in root.iter() if _local(child.tag) == "item"]

    items: list[FeedItem] = []
    for entry in entries:
        title = clean_text(_child_text(entry, "title"))[:300]
        link = _atom_link(entry) or _child_text(entry, "link")
        canonical = canonicalize_url(link)
        if not title or not canonical:
            continue
        excerpt = clean_text(_first_text(entry, ("description", "summary", "content", "encoded")))[
            :280
        ]
        published = parse_datetime(_first_text(entry, ("pubdate", "published", "updated", "date")))
        publisher = clean_publisher(
            _first_text(entry, ("author", "creator", "source")),
            publisher_default or source_name,
        )
        items.append(
            FeedItem(
                title=title,
                link=canonical,
                published_at=published,
                excerpt=excerpt,
                publisher=publisher,
            )
        )
    return items
