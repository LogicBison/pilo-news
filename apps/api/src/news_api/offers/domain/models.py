from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class OfferDefinition:
    industry: str
    offer_slug: str
    name: str
    adapter: str
    scope: str
    cadence: dict[str, Any]
    lookback_days: int
    max_rows: int
    agency_slugs: tuple[str, ...] = ()
    banned_claims: tuple[str, ...] = ()
    enabled: bool = True

    @property
    def cadence_label(self) -> str:
        kind = str(self.cadence.get("kind", "monthly"))
        if kind == "weekly":
            return "weekly"
        if kind == "monthly":
            return "monthly"
        return kind


@dataclass(frozen=True)
class RawRecord:
    title: str
    date: str
    jurisdiction: str
    action: str
    source_name: str
    source_url: str
    summary: str = ""


@dataclass
class AdapterResult:
    records: list[RawRecord] = field(default_factory=list)
    source_version: str = ""
    source_count: int = 0


@dataclass
class OfferRow:
    headline: str
    change: str
    date: str
    jurisdiction: str
    action: str
    source_name: str
    source_url: str

    def as_dict(self) -> dict[str, str]:
        return {
            "headline": self.headline,
            "change": self.change,
            "date": self.date,
            "jurisdiction": self.jurisdiction,
            "action": self.action,
            "source_name": self.source_name,
            "source_url": self.source_url,
        }


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None
