from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from news_api.offers.infrastructure.federal_register import (
    build_url,
    parse_federal_register,
)
from news_api.offers.infrastructure.kev import parse_kev

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "offers"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_kev_filters_since_and_falls_back_to_nvd() -> None:
    payload = load("kev.json")
    payload["vulnerabilities"].append(
        {
            "cveID": "CVE-2026-1002",
            "vendorProject": "Late",
            "product": "Appliance",
            "vulnerabilityName": "Late Appliance Flaw",
            "dateAdded": "2026-11-05",
            "shortDescription": "Added after the issue date.",
            "requiredAction": "Update.",
            "notes": "https://example.org/late",
        }
    )
    result = parse_kev(payload, since=date(2026, 10, 1), until=date(2026, 11, 4))
    assert result.source_version == "2026.11.06"
    assert len(result.records) == 2
    assert result.records[0].date == "2026-11-04"
    assert result.records[1].source_url == "https://nvd.nist.gov/vuln/detail/CVE-2026-1001"
    assert "CVE-2026-1000" in result.records[0].source_name


def test_federal_register_keeps_dated_rows_and_drops_old_ones() -> None:
    payload = load("federal_register.json")
    payload["results"].append(
        {
            "title": "Published after the issue",
            "publication_date": "2026-11-04",
            "effective_on": "2026-12-10",
            "comments_close_on": None,
            "html_url": "https://www.federalregister.gov/documents/2026/11/04/late",
            "citation": "91 FR 3",
            "agencies": [{"name": "Agency D"}],
            "type": "Rule",
            "abstract": "Late.",
        }
    )
    result = parse_federal_register(payload, issue_date=date(2026, 11, 3))
    assert result.source_version == "3"
    assert len(result.records) == 2
    assert result.records[0].date == "2026-11-20"
    assert result.records[0].action == "Comment window closes"
    assert result.records[1].date == "2026-12-01"
    assert result.records[1].action == "Takes effect"
    assert all(
        record.source_url.startswith("https://www.federalregister.gov/")
        for record in result.records
    )


def test_federal_register_url_carries_scope_and_fields() -> None:
    url = build_url(since=date(2026, 8, 1), until=date(2026, 11, 3))
    assert "conditions%5Btype%5D%5B%5D=RULE" in url
    assert "conditions%5Bpublication_date%5D%5Bgte%5D=2026-08-01" in url
    assert "conditions%5Bpublication_date%5D%5Blte%5D=2026-11-03" in url
    assert "fields%5B%5D=effective_on" in url
