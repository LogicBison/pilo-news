"""Portfolio export: the source list in the format feed readers speak.

OPML is what an operator can hand to a colleague, import into a reader, or
diff between environments. It is also the format discovery accepts, so an
export and an import round-trip.
"""

from __future__ import annotations

from typing import Any
from xml.etree import ElementTree


def to_opml(rows: list[dict[str, Any]], *, title: str = "System News sources") -> str:
    opml = ElementTree.Element("opml", {"version": "2.0"})
    head = ElementTree.SubElement(opml, "head")
    ElementTree.SubElement(head, "title").text = title
    body = ElementTree.SubElement(opml, "body")

    by_industry: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_industry.setdefault(str(row.get("industry") or "unassigned"), []).append(row)

    for industry, sources in sorted(by_industry.items()):
        group = ElementTree.SubElement(body, "outline", {"text": industry, "title": industry})
        for source in sources:
            ElementTree.SubElement(
                group,
                "outline",
                {
                    "type": "rss",
                    "text": str(source.get("name") or source.get("feed_url")),
                    "title": str(source.get("name") or ""),
                    "xmlUrl": str(source.get("feed_url") or ""),
                    "language": str(source.get("language") or ""),
                },
            )
    ElementTree.indent(opml, space="  ")
    return ElementTree.tostring(opml, encoding="unicode") + "\n"
