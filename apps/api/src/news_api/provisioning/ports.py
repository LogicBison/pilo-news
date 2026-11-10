"""Ports for the deployment-profile importer.

This module is the boundary between provisioning and the rest of the system:
it re-exports the pure channel/feed vocabulary and declares the repository
protocols that `apply_profile` depends on. Provisioning code imports from here
only, never from another context's `infrastructure` or `domain` modules.
"""

from __future__ import annotations

from typing import Any, Protocol

from news_api.channels.domain.theme import (
    DEFAULT_THEMES,
    Channel,
    is_reserved_slug,
    validate_theme,
)
from news_api.platform.i18n import SUPPORTED_LOCALES
from news_api.sources.application.quality import coverage_warnings
from news_api.sources.domain.models import Source
from news_api.sources.domain.validation import normalize_feed_url, validate_feed_url

__all__ = [
    "DEFAULT_THEMES",
    "SUPPORTED_LOCALES",
    "CatalogRepository",
    "Channel",
    "ChannelRepository",
    "Repositories",
    "SettingsPort",
    "Source",
    "SourceRepository",
    "coverage_warnings",
    "is_reserved_slug",
    "normalize_feed_url",
    "validate_feed_url",
    "validate_theme",
]


class ChannelRepository(Protocol):
    async def get_channel(
        self, slug: str, locale: str = "en", *, enabled_only: bool = True
    ) -> Channel | None: ...

    async def create_channel(
        self,
        *,
        slug: str,
        code: str,
        name: str,
        theme: dict[str, Any],
        locales: dict[str, dict[str, str]],
        disclaimers: dict[str, str],
        cta: dict[str, Any],
        timezone: str,
        retention_days: int,
        sort_order: int,
        enabled: bool,
        topics: list[dict[str, Any]],
    ) -> Channel | None: ...

    async def update_channel(
        self,
        slug: str,
        *,
        name: str | None = None,
        enabled: bool | None = None,
        theme: dict[str, Any] | None = None,
        disclaimers: dict[str, Any] | None = None,
        cta: dict[str, Any] | None = None,
        timezone: str | None = None,
        retention_days: int | None = None,
        sort_order: int | None = None,
    ) -> bool: ...

    async def list_locales(self, slug: str) -> dict[str, dict[str, str]]: ...

    async def upsert_locales(self, slug: str, locales: dict[str, dict[str, str]]) -> None: ...


class SourceRepository(Protocol):
    async def list_sources(
        self, industry_id: str | None = None, *, include_disabled: bool = True
    ) -> list[Source]: ...

    async def create_source(
        self,
        *,
        industry_id: str,
        name: str,
        feed_url: str,
        language: str,
        trust: float,
        enabled: bool,
        allow_http: bool,
        poll_interval_min: int,
        terms_checked_at: str | None,
        terms_url: str | None,
        permission_state: str = "unknown",
        auth_type: str = "none",
        auth_header_name: str | None = None,
        auth_secret_ref: str | None = None,
        licence_type: str = "unknown",
    ) -> Source | None: ...

    async def update_source(self, source_id: str, fields: dict[str, Any]) -> Source | None: ...


class CatalogRepository(Protocol):
    """Topics and partners owned by the editorial context."""

    async def list_topics_admin(self, industry_id: str) -> list[dict[str, Any]]: ...

    async def create_topic(
        self,
        *,
        industry_id: str,
        slug: str,
        label: dict[str, str],
        weight: float,
        keywords: dict[str, list[str]],
    ) -> dict[str, Any] | None: ...

    async def update_topic(
        self, topic_id: str, fields: dict[str, Any]
    ) -> dict[str, Any] | None: ...

    async def list_partners(self, industry_id: str | None = None) -> list[dict[str, Any]]: ...

    async def create_partner(
        self, *, industry_id: str, name: str, contact_email: str, regions: list[str]
    ) -> dict[str, Any] | None: ...

    async def update_partner(
        self, partner_id: str, fields: dict[str, Any]
    ) -> dict[str, Any] | None: ...


class SettingsPort(Protocol):
    refresh_interval_minutes: int


class Repositories(Protocol):
    """The collaborators `apply_profile` needs; composed in `adapters`.

    Declared as read-only properties so immutable implementations (frozen
    dataclasses, simple namespaces) satisfy the protocol.
    """

    @property
    def channels(self) -> ChannelRepository: ...

    @property
    def sources(self) -> SourceRepository: ...

    @property
    def catalog(self) -> CatalogRepository: ...

    @property
    def settings(self) -> SettingsPort: ...
