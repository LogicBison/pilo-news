from __future__ import annotations

from datetime import date

from news_api.offers.domain.models import AdapterResult, OfferDefinition
from news_api.offers.infrastructure.federal_register import fetch_federal_register
from news_api.offers.infrastructure.kev import fetch_kev

ADAPTER_NAMES = ("cisa_kev", "federal_register")


def adapter_names() -> tuple[str, ...]:
    return ADAPTER_NAMES


async def fetch_records(
    definition: OfferDefinition, *, since: date, issue_date: date
) -> AdapterResult:
    if definition.adapter == "cisa_kev":
        return await fetch_kev(since=since, until=issue_date)
    if definition.adapter == "federal_register":
        return await fetch_federal_register(
            since=since, issue_date=issue_date, agency_slugs=definition.agency_slugs
        )
    raise ValueError(f"unknown offer adapter '{definition.adapter}'")
