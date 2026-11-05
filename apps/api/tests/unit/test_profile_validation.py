"""Unit tests for deployment-profile loading and validation (no database)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from news_api.provisioning.application.apply import (
    ProfileError,
    load_profile,
    validate_profile,
)
from news_api.provisioning.domain.profile import DeploymentProfile


def base_payload(**industry_overrides: Any) -> dict[str, Any]:
    industry: dict[str, Any] = {
        "slug": "sample",
        "code": "SAMPLE",
        "name": "Sample Industry",
        "theme": {"layout": "editorial"},
        "sources": [{"name": "Feed", "feed_url": "https://example.org/feed.xml"}],
    }
    industry.update(industry_overrides)
    return {"brand": "Sample", "industries": [industry]}


def profile(**industry_overrides: Any) -> DeploymentProfile:
    return DeploymentProfile.model_validate(base_payload(**industry_overrides))


def test_valid_profile_passes_validation() -> None:
    loaded = profile()
    validate_profile(loaded, loaded.industries)


def test_reserved_slug_is_rejected() -> None:
    loaded = profile(slug="admin")
    with pytest.raises(ProfileError, match="slug is reserved"):
        validate_profile(loaded, loaded.industries)


def test_low_contrast_theme_is_rejected() -> None:
    loaded = profile(theme={"layout": "editorial", "text": "#ffffff", "bg": "#ffffff"})
    with pytest.raises(ProfileError, match="contrast"):
        validate_profile(loaded, loaded.industries)


def test_http_feed_requires_allow_http() -> None:
    loaded = profile(sources=[{"name": "Feed", "feed_url": "http://example.org/feed.xml"}])
    with pytest.raises(ProfileError, match="allow_http"):
        validate_profile(loaded, loaded.industries)


def test_duplicate_feed_url_is_rejected() -> None:
    source = {"name": "Feed", "feed_url": "https://example.org/feed.xml"}
    loaded = profile(sources=[source, source])
    with pytest.raises(ProfileError, match="duplicate feed_url"):
        validate_profile(loaded, loaded.industries)


def test_unsupported_locale_is_rejected() -> None:
    loaded = profile(locales={"fr": {"name": "Français"}})
    with pytest.raises(ProfileError, match="unsupported locale"):
        validate_profile(loaded, loaded.industries)


def test_duplicate_industry_slug_fails_schema() -> None:
    payload = base_payload()
    payload["industries"].append(base_payload()["industries"][0])
    with pytest.raises(ValidationError, match="duplicate industry slug"):
        DeploymentProfile.model_validate(payload)


def test_load_profile_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ProfileError, match="profile not found"):
        load_profile(tmp_path / "missing.json")


def test_load_profile_reports_bad_json(tmp_path: Path) -> None:
    path = tmp_path / "profile.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ProfileError, match="not valid JSON"):
        load_profile(path)


def test_load_profile_example_file_is_valid() -> None:
    example = Path(__file__).resolve().parents[2] / "config" / "deployment.example.json"
    loaded = load_profile(example)
    assert loaded.brand == "System News"
    assert {industry.slug for industry in loaded.industries} == {"legal", "financial"}
    validate_profile(loaded, loaded.industries)


def test_example_profile_matches_seeded_themes() -> None:
    example = Path(__file__).resolve().parents[2] / "config" / "deployment.example.json"
    loaded = json.loads(example.read_text(encoding="utf-8"))
    layouts = {item["slug"]: item["theme"]["layout"] for item in loaded["industries"]}
    assert layouts == {"legal": "editorial", "financial": "professional"}
