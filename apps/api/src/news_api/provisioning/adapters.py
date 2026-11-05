"""Composition root for the deployment-profile importer.

This is the only module in `provisioning` that knows which concrete context
implements each port. Swap these for fakes in tests by passing a different
`Repositories` object into `apply_profile`.
"""

from __future__ import annotations

from dataclasses import dataclass

from news_api.channels.infrastructure import repo as channels_repo
from news_api.editorial.infrastructure import ops_repo
from news_api.platform.settings import get_settings
from news_api.provisioning.ports import (
    CatalogRepository,
    ChannelRepository,
    SettingsPort,
    SourceRepository,
)
from news_api.sources.infrastructure import repo as sources_repo


@dataclass(frozen=True)
class DefaultRepositories:
    channels: ChannelRepository
    sources: SourceRepository
    catalog: CatalogRepository
    settings: SettingsPort


def default_repositories() -> DefaultRepositories:
    return DefaultRepositories(
        channels=channels_repo,
        sources=sources_repo,
        catalog=ops_repo,
        settings=get_settings(),
    )
