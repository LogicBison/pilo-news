"""Unit tests for the profile importer against injected ports (no database)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from news_api.channels.domain.theme import Channel
from news_api.provisioning.application.apply import apply_profile
from news_api.provisioning.domain.profile import DeploymentProfile


class FakeSettings:
    refresh_interval_minutes = 720


class FakeChannels:
    def __init__(self) -> None:
        self.rows: dict[str, Channel] = {}
        self.locales: dict[str, dict[str, dict[str, str]]] = {}
        self.catalog: FakeCatalog | None = None
        self.writes = 0

    async def get_channel(
        self, slug: str, locale: str = "en", *, enabled_only: bool = True
    ) -> Channel | None:
        return self.rows.get(slug)

    async def create_channel(self, **kwargs: Any) -> Channel | None:
        self.writes += 1
        channel = Channel(
            id=f"id-{kwargs['slug']}",
            slug=kwargs["slug"],
            code=kwargs["code"],
            name=kwargs["name"],
            base_name=kwargs["name"],
            tagline=kwargs["locales"].get("en", {}).get("tagline", ""),
            theme=kwargs["theme"],
            locales=list(kwargs["locales"]),
            disclaimers=kwargs["disclaimers"],
            cta=kwargs["cta"],
            timezone=kwargs["timezone"],
            retention_days=kwargs["retention_days"],
            enabled=kwargs["enabled"],
            sort_order=kwargs["sort_order"],
        )
        self.rows[channel.slug] = channel
        self.locales[channel.slug] = {key: dict(value) for key, value in kwargs["locales"].items()}
        # Mirror the real create_channel, which seeds profile topics with the channel.
        if self.catalog is not None:
            for index, topic in enumerate(kwargs.get("topics", [])):
                self.catalog.topics.setdefault(channel.id, []).append(
                    {
                        "id": f"topic-{index}",
                        "slug": topic["slug"],
                        "label": topic.get("label", {}),
                        "weight": float(topic.get("weight", 1.0)),
                        "keywords": topic.get("keywords", {}),
                    }
                )
        return channel

    async def update_channel(self, slug: str, **fields: Any) -> bool:
        self.writes += 1
        current = self.rows[slug]
        self.rows[slug] = Channel(
            **{
                **current.__dict__,
                "base_name": fields.get("name") or current.base_name,
                "theme": fields.get("theme") or current.theme,
                "disclaimers": fields.get("disclaimers") or current.disclaimers,
                "cta": fields.get("cta") or current.cta,
                "timezone": fields.get("timezone") or current.timezone,
                "retention_days": fields.get("retention_days") or current.retention_days,
                "sort_order": fields.get("sort_order") or current.sort_order,
                "enabled": current.enabled if fields.get("enabled") is None else fields["enabled"],
            }
        )
        return True

    async def list_locales(self, slug: str) -> dict[str, dict[str, str]]:
        return dict(self.locales.get(slug, {}))

    async def upsert_locales(self, slug: str, locales: dict[str, dict[str, str]]) -> None:
        self.writes += 1
        self.locales.setdefault(slug, {}).update(locales)


class FakeSources:
    def __init__(self) -> None:
        self.rows: list[SimpleNamespace] = []
        self.writes = 0

    async def list_sources(
        self, industry_id: str | None = None, *, include_disabled: bool = True
    ) -> list[SimpleNamespace]:
        return [row for row in self.rows if row.industry_id == industry_id]

    async def create_source(self, **kwargs: Any) -> SimpleNamespace:
        self.writes += 1
        row = SimpleNamespace(id=f"src-{len(self.rows)}", **kwargs)
        self.rows.append(row)
        return row

    async def update_source(self, source_id: str, fields: dict[str, Any]) -> SimpleNamespace:
        self.writes += 1
        row = next(item for item in self.rows if item.id == source_id)
        for key, value in fields.items():
            setattr(row, key, value)
        return row


class FakeCatalog:
    def __init__(self) -> None:
        self.topics: dict[str, list[dict[str, Any]]] = {}
        self.partners: dict[str, dict[str, Any]] = {}
        self.writes = 0

    async def list_topics_admin(self, industry_id: str) -> list[dict[str, Any]]:
        return self.topics.get(industry_id, [])

    async def create_topic(self, **kwargs: Any) -> dict[str, Any]:
        self.writes += 1
        row = {
            "id": f"topic-{len(self.topics)}",
            "slug": kwargs["slug"],
            "label": kwargs["label"],
            "weight": kwargs["weight"],
            "keywords": kwargs["keywords"],
        }
        self.topics.setdefault(kwargs["industry_id"], []).append(row)
        return row

    async def update_topic(self, topic_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        self.writes += 1
        for rows in self.topics.values():
            for row in rows:
                if row["id"] == topic_id:
                    row.update(fields)
                    return row
        raise AssertionError("topic not found")

    async def list_partners(self, industry_id: str | None = None) -> list[dict[str, Any]]:
        if industry_id and industry_id in self.partners:
            return [self.partners[industry_id]]
        return []

    async def create_partner(self, **kwargs: Any) -> dict[str, Any]:
        self.writes += 1
        row = {"id": "partner-1", "weight": 1.0, "regions": kwargs["regions"], **kwargs}
        self.partners[kwargs["industry_id"]] = row
        return row

    async def update_partner(self, partner_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        self.writes += 1
        row = next(iter(self.partners.values()))
        row.update(fields)
        return row


def repositories() -> SimpleNamespace:
    catalog = FakeCatalog()
    channels = FakeChannels()
    channels.catalog = catalog
    return SimpleNamespace(
        channels=channels,
        sources=FakeSources(),
        catalog=catalog,
        settings=FakeSettings(),
    )


def profile_payload() -> dict[str, Any]:
    return {
        "brand": "Fake News",
        "default_industry": "fake",
        "industries": [
            {
                "slug": "fake",
                "code": "FAKE",
                "name": "Fake Industry",
                "theme": {"layout": "professional"},
                "locales": {"en": {"name": "Fake Industry", "tagline": "Fake."}},
                "sources": [{"name": "Fake Feed", "feed_url": "https://example.org/fake.xml"}],
                "topics": [{"slug": "fakes", "label": {"en": "Fakes"}}],
                "partner": {"name": "Fake Partner", "contact_email": "partner@example.org"},
            }
        ],
    }


@pytest.mark.asyncio
async def test_profile_import_runs_entirely_against_injected_ports() -> None:
    repos = repositories()
    profile = DeploymentProfile.model_validate(profile_payload())

    first = await apply_profile(profile, repos=repos)
    writes_after_first = repos.channels.writes + repos.sources.writes + repos.catalog.writes
    assert first["totals"]["created"] == 5
    assert repos.channels.writes == 1
    assert repos.sources.writes == 1
    assert repos.catalog.writes == 1

    second = await apply_profile(profile, repos=repos)
    writes_after_second = repos.channels.writes + repos.sources.writes + repos.catalog.writes
    assert second["totals"] == {"created": 0, "updated": 0, "skipped": 5}
    assert writes_after_second == writes_after_first


@pytest.mark.asyncio
async def test_dry_run_with_injected_ports_writes_nothing() -> None:
    repos = repositories()
    report = await apply_profile(
        DeploymentProfile.model_validate(profile_payload()), repos=repos, dry_run=True
    )

    assert report["totals"]["created"] == 5
    assert repos.channels.writes == 0
    assert repos.sources.writes == 0
    assert repos.catalog.writes == 0
