"""Integration tests for the deployment-profile import (apply-profile)."""

from __future__ import annotations

from typing import Any

import pytest

from news_api.channels.infrastructure import repo as channels_repo
from news_api.editorial.infrastructure import ops_repo
from news_api.provisioning.application.apply import apply_profile
from news_api.provisioning.domain.profile import DeploymentProfile
from news_api.sources.infrastructure import repo as sources_repo


def profile_payload(slug: str = "e2e-deploy", **industry_overrides: Any) -> dict[str, Any]:
    industry: dict[str, Any] = {
        "slug": slug,
        "code": "E2E_DEPLOY",
        "name": "E2E Deploy",
        "theme": {"layout": "academic"},
        "locales": {
            "en": {"name": "E2E Deploy", "tagline": "Deployment profile channel."},
            "es": {"name": "Despliegue E2E", "tagline": "Canal de perfil de despliegue."},
        },
        "disclaimers": {
            "en": "News, not advice.",
            "es": "Noticias, no asesoría.",
        },
        "topics": [
            {
                "slug": "standards",
                "label": {"en": "Standards", "es": "Normas"},
                "weight": 1.25,
                "keywords": {"en": ["standard"], "es": ["norma"]},
            }
        ],
        "sources": [
            {
                "name": "E2E Feed EN",
                "feed_url": "https://example.org/e2e-feed-en.xml",
                "language": "en",
                "trust": 0.81,
            },
            {
                "name": "E2E Feed ES",
                "feed_url": "https://example.org/e2e-feed-es.xml",
                "language": "es",
                "trust": 0.77,
            },
        ],
        "partner": {
            "name": "E2E Partner",
            "contact_email": "partner@example.org",
            "regions": ["latam"],
        },
    }
    industry.update(industry_overrides)
    return {
        "brand": "E2E News",
        "site_url": "https://e2e.example.org",
        "default_locale": "en",
        "default_industry": slug,
        "industries": [industry],
    }


def build_profile(**industry_overrides: Any) -> DeploymentProfile:
    return DeploymentProfile.model_validate(profile_payload(**industry_overrides))


@pytest.mark.asyncio
async def test_apply_profile_creates_every_entity() -> None:
    report = await apply_profile(build_profile())

    assert report["totals"]["created"] == 7
    assert report["totals"]["updated"] == 0
    channel = await channels_repo.get_channel("e2e-deploy", enabled_only=False)
    assert channel is not None
    assert channel.theme["layout"] == "academic"
    assert channel.timezone == "America/El_Salvador"
    assert channel.locales == ["en", "es"]

    locales = await channels_repo.list_locales("e2e-deploy")
    assert locales["es"]["name"] == "Despliegue E2E"

    topics = await ops_repo.list_topics_admin(channel.id)
    assert [str(row["slug"]) for row in topics] == ["standards"]
    assert float(topics[0]["weight"]) == pytest.approx(1.25)

    sources = await sources_repo.list_sources(channel.id)
    assert {source.feed_url for source in sources} == {
        "https://example.org/e2e-feed-en.xml",
        "https://example.org/e2e-feed-es.xml",
    }
    assert {source.language: source.trust for source in sources}["en"] == pytest.approx(0.81)

    partners = await ops_repo.list_partners(channel.id)
    assert partners[0]["name"] == "E2E Partner"
    assert partners[0]["contact_email"] == "partner@example.org"


@pytest.mark.asyncio
async def test_apply_profile_is_idempotent_on_second_run() -> None:
    profile = build_profile()
    await apply_profile(profile)
    second = await apply_profile(profile)

    assert second["totals"] == {"created": 0, "updated": 0, "skipped": 7}
    assert second["industries"][0]["state"] == "unchanged"


@pytest.mark.asyncio
async def test_apply_profile_updates_changed_fields_without_touching_other_channels() -> None:
    await apply_profile(build_profile())
    changed = build_profile(
        name="E2E Deploy Renamed",
        sources=[
            {
                "name": "E2E Feed EN",
                "feed_url": "https://example.org/e2e-feed-en.xml",
                "language": "en",
                "trust": 0.95,
            }
        ],
    )
    report = await apply_profile(changed)

    assert report["totals"]["updated"] == 2
    assert report["totals"]["created"] == 0
    channel = await channels_repo.get_channel("e2e-deploy", enabled_only=False)
    assert channel is not None
    assert channel.base_name == "E2E Deploy Renamed"
    sources = await sources_repo.list_sources(channel.id)
    assert {source.feed_url: source.trust for source in sources} == {
        "https://example.org/e2e-feed-en.xml": pytest.approx(0.95),
        "https://example.org/e2e-feed-es.xml": pytest.approx(0.77),
    }


@pytest.mark.asyncio
async def test_apply_profile_dry_run_writes_nothing() -> None:
    report = await apply_profile(build_profile(), dry_run=True)

    assert report["dry_run"] is True
    assert report["totals"]["created"] == 7
    assert await channels_repo.get_channel("e2e-deploy", enabled_only=False) is None


@pytest.mark.asyncio
async def test_apply_profile_scopes_to_one_industry() -> None:
    await apply_profile(build_profile())
    second = profile_payload(slug="e2e-other")
    payload = build_profile().model_dump()
    payload["industries"].append(
        DeploymentProfile.model_validate(second).industries[0].model_dump()
    )
    profile = DeploymentProfile.model_validate(payload)

    report = await apply_profile(profile, only_industry="e2e-other")

    assert [item["slug"] for item in report["industries"]] == ["e2e-other"]
    assert report["totals"]["created"] == 7
    assert await channels_repo.get_channel("e2e-deploy", enabled_only=False) is not None
    assert await channels_repo.get_channel("e2e-other", enabled_only=False) is not None
