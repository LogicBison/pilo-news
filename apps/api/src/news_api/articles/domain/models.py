from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Topic:
    id: str
    slug: str
    weight: float
    keywords: dict[str, list[str]]
    label: dict[str, str]

    def keywords_for(self, language: str) -> list[str]:
        values = self.keywords.get(language) or self.keywords.get("en") or []
        return [str(value).casefold() for value in values if str(value).strip()]

    def label_for(self, locale: str) -> str:
        return str(self.label.get(locale) or self.label.get("en") or self.slug)


@dataclass
class Candidate:
    industry_id: str
    source_id: str | None
    source_name: str
    source_trust: float
    title: str
    url: str
    canonical_url: str
    excerpt: str
    publisher: str
    language: str
    published_at: datetime
    pinned: bool = False
    is_seed: bool = False
    seed_topics: tuple[str, ...] = ()
    article_id: str = ""
    score: float = 0.0
    topics: list[Topic] = field(default_factory=list)
    corroboration: int = 1
    corroborating_sources: list[str] = field(default_factory=list)
    verification: str = "trusted-source"


@dataclass(frozen=True)
class FeedItem:
    title: str
    link: str
    published_at: datetime
    excerpt: str
    publisher: str


@dataclass(frozen=True)
class FetchOutcome:
    source_id: str
    source_name: str
    status: str
    items: list[FeedItem]
    etag: str | None = None
    last_modified: str | None = None
    error: str | None = None
    blocked: bool = False


def topic_from_row(row: dict[str, Any]) -> Topic:
    from news_api.platform.jsons import as_dict

    return Topic(
        id=str(row["id"]),
        slug=str(row["slug"]),
        weight=float(row["weight"]),
        keywords={key: list(value) for key, value in as_dict(row["keywords"]).items()},
        label={key: str(value) for key, value in as_dict(row["label"]).items()},
    )
