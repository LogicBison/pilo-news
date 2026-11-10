from __future__ import annotations

from typing import Any

from news_api.offers.domain.models import OfferDefinition
from news_api.platform.config import load_json

REQUIRED = ("offer_slug", "name", "adapter", "scope", "cadence")


def _definition(industry: str, raw: dict[str, Any]) -> OfferDefinition:
    missing = [key for key in REQUIRED if not raw.get(key)]
    if missing:
        raise ValueError(f"offer definition {industry}: missing {', '.join(missing)}")
    cadence = raw.get("cadence")
    if not isinstance(cadence, dict):
        raise ValueError(f"offer definition {industry}: cadence must be an object")
    scope = str(raw["scope"]).strip()
    if not scope:
        raise ValueError(f"offer definition {industry}: scope is empty")
    return OfferDefinition(
        industry=industry,
        offer_slug=str(raw["offer_slug"]),
        name=str(raw["name"]),
        adapter=str(raw["adapter"]),
        scope=scope,
        cadence=cadence,
        lookback_days=int(raw.get("lookback_days", 30)),
        max_rows=max(1, min(int(raw.get("max_rows", 12)), 30)),
        agency_slugs=tuple(
            str(item).strip() for item in (raw.get("agency_slugs") or []) if str(item).strip()
        ),
        banned_claims=tuple(
            str(item).strip().lower()
            for item in (raw.get("banned_claims") or [])
            if str(item).strip()
        ),
        enabled=bool(raw.get("enabled", True)),
        standfirst_noun=str(raw.get("standfirst_noun") or "changes").strip() or "changes",
    )


def load_definitions() -> dict[str, OfferDefinition]:
    payload = load_json("offers.json")
    definitions: dict[str, OfferDefinition] = {}
    for industry, raw in payload.items():
        if not isinstance(raw, dict):
            raise ValueError(f"offer definition {industry}: must be an object")
        definition = _definition(str(industry), raw)
        definitions[definition.industry] = definition
    return definitions


def definition_for(industry: str, offer_slug: str | None = None) -> OfferDefinition | None:
    definition = load_definitions().get(industry)
    if not definition:
        return None
    if offer_slug and definition.offer_slug != offer_slug:
        return None
    return definition
