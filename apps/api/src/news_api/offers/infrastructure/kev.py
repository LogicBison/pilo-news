from __future__ import annotations

import re
from datetime import date
from typing import Any

from news_api.offers.domain.models import AdapterResult, RawRecord, parse_iso_date
from news_api.offers.infrastructure.fetch import fetch_json

SOURCE_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
URL_RE = re.compile(r"https?://[^\s;]+")


def parse_kev(payload: dict[str, Any], *, since: date, until: date | None = None) -> AdapterResult:
    rows: list[RawRecord] = []
    for item in payload.get("vulnerabilities") or []:
        if not isinstance(item, dict):
            continue
        added = parse_iso_date(str(item.get("dateAdded") or ""))
        if not added or added < since:
            continue
        if until is not None and added > until:
            continue
        cve = str(item.get("cveID") or "").strip()
        vendor = str(item.get("vendorProject") or "").strip()
        product = str(item.get("product") or "").strip()
        title = str(item.get("vulnerabilityName") or "").strip() or f"{vendor} {product}"
        action = str(item.get("requiredAction") or "").strip()
        if not action:
            action = f"Apply the vendor update for {cve}."
        notes = str(item.get("notes") or "")
        match = URL_RE.search(notes)
        url = match.group(0) if match else f"https://nvd.nist.gov/vuln/detail/{cve}"
        rows.append(
            RawRecord(
                title=f"{vendor} {product}: {title}".strip(": "),
                date=added.isoformat(),
                jurisdiction="global",
                action=action,
                source_name=f"CISA KEV ({cve})",
                source_url=url,
                summary=str(item.get("shortDescription") or "").strip(),
            )
        )
    rows.sort(key=lambda row: row.date, reverse=True)
    return AdapterResult(
        records=rows,
        source_version=str(payload.get("catalogVersion") or ""),
        source_count=len(payload.get("vulnerabilities") or []),
    )


async def fetch_kev(*, since: date, until: date | None = None) -> AdapterResult:
    payload = await fetch_json(SOURCE_URL)
    return parse_kev(payload, since=since, until=until)
