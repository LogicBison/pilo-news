"""Idempotent deployment-profile import.

`apply_profile` reconciles a profile against the database: it creates what is
missing and updates what differs, but never deletes operator data (sources,
articles, pins, leads, or removed channels). Running it twice with the same
profile produces only `skipped` actions on the second run.

Persistence is reached through `Repositories` (see `ports.py`); the default
wiring lives in `adapters.py`, so tests can inject fakes.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from news_api.platform.jsons import as_dict
from news_api.provisioning.domain.profile import (
    DeploymentProfile,
    IndustryProfile,
    PartnerProfile,
    SourceProfile,
    TopicProfile,
)
from news_api.provisioning.ports import (
    DEFAULT_THEMES,
    SUPPORTED_LOCALES,
    Repositories,
    coverage_warnings,
    is_reserved_slug,
    normalize_feed_url,
    validate_feed_url,
    validate_theme,
)


class ProfileError(ValueError):
    """Operator-facing profile problem; the message is safe to print."""


def load_profile(path: Path) -> DeploymentProfile:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProfileError(f"profile not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ProfileError(
            f"profile is not valid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}"
        ) from exc
    try:
        return DeploymentProfile.model_validate(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        location = ".".join(str(part) for part in first["loc"]) or "profile"
        raise ProfileError(f"{location}: {first['msg']}") from exc


def resolve_theme(theme: dict[str, Any]) -> dict[str, Any]:
    layout = str(theme.get("layout", "editorial"))
    base = DEFAULT_THEMES.get(layout, DEFAULT_THEMES["editorial"])
    return {**base, **theme}


def validate_profile(profile: DeploymentProfile, industries: list[IndustryProfile]) -> None:
    problems: list[str] = []
    slugs = {industry.slug for industry in profile.industries}
    if profile.default_industry and profile.default_industry not in slugs:
        problems.append(f"default_industry '{profile.default_industry}' is not in the profile")
    for industry in industries:
        prefix = industry.slug
        if is_reserved_slug(industry.slug):
            problems.append(f"{prefix}: slug is reserved")
        for problem in validate_theme(resolve_theme(industry.theme)):
            problems.append(f"{prefix}: {problem}")
        for locale in sorted(set(industry.locales) | set(industry.disclaimers)):
            if locale not in SUPPORTED_LOCALES:
                problems.append(f"{prefix}: unsupported locale '{locale}'")
        feeds: set[str] = set()
        for source in industry.sources:
            if source.language not in SUPPORTED_LOCALES:
                problems.append(
                    f"{prefix}: source '{source.name}' has unsupported language "
                    f"'{source.language}'"
                )
            url = normalize_feed_url(source.feed_url)
            for problem in validate_feed_url(url, allow_http=source.allow_http):
                problems.append(f"{prefix}: {problem}")
            if url in feeds:
                problems.append(f"{prefix}: duplicate feed_url {url}")
            feeds.add(url)
    if problems:
        raise ProfileError("; ".join(problems))


async def apply_profile(
    profile: DeploymentProfile,
    *,
    dry_run: bool = False,
    only_industry: str | None = None,
    repos: Repositories | None = None,
) -> dict[str, Any]:
    if repos is None:
        from news_api.provisioning.adapters import default_repositories

        repos = default_repositories()

    selected = profile.industries
    if only_industry is not None:
        selected = [item for item in profile.industries if item.slug == only_industry]
        if not selected:
            raise ProfileError(f"industry '{only_industry}' is not in the profile")
    validate_profile(profile, selected)

    report: dict[str, Any] = {
        "dry_run": dry_run,
        "brand": profile.brand,
        "site_url": profile.site_url,
        "default_industry": profile.default_industry,
        "industries": [],
        "totals": {"created": 0, "updated": 0, "skipped": 0},
        "warnings": [],
    }
    if profile.refresh_interval_minutes != repos.settings.refresh_interval_minutes:
        report["warnings"].append(
            f"refresh_interval_minutes={profile.refresh_interval_minutes} is not applied at "
            "runtime; set REFRESH_INTERVAL_MINUTES in .env.<env> "
            f"(current {repos.settings.refresh_interval_minutes})"
        )
    for industry in selected:
        result = await _apply_industry(industry, dry_run=dry_run, repos=repos)
        report["industries"].append(result)
        for key in ("created", "updated", "skipped"):
            report["totals"][key] += result["counts"][key]
        for warning in result.get("coverage", []):
            report["warnings"].append(f"{industry.slug}: {warning}")
    return report


async def _apply_industry(
    industry: IndustryProfile, *, dry_run: bool, repos: Repositories
) -> dict[str, Any]:
    actions: list[dict[str, str]] = []

    def record(entity: str, key: str, action: str) -> None:
        actions.append({"entity": entity, "key": key, "action": action})

    theme = resolve_theme(industry.theme)
    locales = industry.locale_names or {
        "en": {"name": industry.name, "tagline": ""},
        "es": {"name": industry.name, "tagline": ""},
    }
    disclaimers = industry.disclaimers or {
        "en": "News, not professional advice.",
        "es": "Noticias, no asesoría profesional.",
    }

    channel = await repos.channels.get_channel(industry.slug, enabled_only=False)
    new_channel = channel is None
    state = "unchanged"
    industry_id = channel.id if channel else None

    if new_channel:
        record("industry", industry.slug, "created")
        for locale in locales:
            record("locale", locale, "created")
        state = "created"
        if not dry_run:
            channel = await repos.channels.create_channel(
                slug=industry.slug,
                code=industry.code,
                name=industry.name,
                theme=theme,
                locales=locales,
                disclaimers=disclaimers,
                cta=industry.cta,
                timezone=industry.timezone,
                retention_days=industry.retention_days,
                sort_order=industry.sort_order,
                enabled=industry.enabled,
                topics=[topic.model_dump() for topic in industry.topics],
            )
            if channel is None:
                raise ProfileError(f"{industry.slug}: channel could not be created")
            industry_id = channel.id
    else:
        changes = _channel_changes(channel, industry, theme, disclaimers)
        current_locales = await repos.channels.list_locales(industry.slug)
        locale_changes = {
            locale: copy for locale, copy in locales.items() if current_locales.get(locale) != copy
        }
        for locale in locales:
            record("locale", locale, "updated" if locale in locale_changes else "skipped")
        if changes or locale_changes:
            state = "updated"
            record("industry", industry.slug, "updated")
            if not dry_run:
                if changes:
                    await repos.channels.update_channel(
                        industry.slug,
                        name=changes.get("name"),
                        enabled=changes.get("enabled"),
                        theme=changes.get("theme"),
                        disclaimers=changes.get("disclaimers"),
                        cta=changes.get("cta"),
                        timezone=changes.get("timezone"),
                        retention_days=changes.get("retention_days"),
                        sort_order=changes.get("sort_order"),
                    )
                if locale_changes:
                    await repos.channels.upsert_locales(industry.slug, locale_changes)
        else:
            record("industry", industry.slug, "skipped")

    existing_topics: dict[str, dict[str, Any]] = {}
    if industry_id:
        existing_topics = {
            str(row["slug"]): row for row in await repos.catalog.list_topics_admin(industry_id)
        }
    for topic in industry.topics:
        if new_channel:
            # create_channel already seeds the profile topics with the channel row.
            record("topic", topic.slug, "created")
            continue
        row = existing_topics.get(topic.slug)
        if row is None:
            record("topic", topic.slug, "created")
            if not dry_run:
                if industry_id is None:  # pragma: no cover - created above
                    raise ProfileError(f"{industry.slug}: industry row missing")
                await repos.catalog.create_topic(
                    industry_id=industry_id,
                    slug=topic.slug,
                    label=topic.label,
                    weight=topic.weight,
                    keywords=topic.keywords,
                )
        elif _topic_changes(row, topic):
            record("topic", topic.slug, "updated")
            if not dry_run:
                await repos.catalog.update_topic(
                    str(row["id"]),
                    {
                        "label": topic.label,
                        "weight": topic.weight,
                        "keywords": topic.keywords,
                    },
                )
        else:
            record("topic", topic.slug, "skipped")

    existing_sources: dict[str, Any] = {}
    if industry_id:
        existing_sources = {
            normalize_feed_url(source.feed_url): source
            for source in await repos.sources.list_sources(industry_id)
        }
    for source in industry.sources:
        url = normalize_feed_url(source.feed_url)
        found = existing_sources.get(url)
        if found is None:
            record("source", url, "created")
            if not dry_run:
                if industry_id is None:  # pragma: no cover - created above
                    raise ProfileError(f"{industry.slug}: industry row missing")
                await repos.sources.create_source(
                    industry_id=industry_id,
                    name=source.name,
                    feed_url=url,
                    language=source.language,
                    trust=source.trust,
                    enabled=source.enabled,
                    allow_http=source.allow_http,
                    poll_interval_min=source.poll_interval_min,
                    terms_checked_at=None,
                    terms_url=source.terms_url,
                )
        else:
            changes = _source_changes(found, source, url)
            if changes:
                record("source", url, "updated")
                if not dry_run:
                    await repos.sources.update_source(found.id, changes)
            else:
                record("source", url, "skipped")

    if industry.partner is not None:
        await _apply_partner(
            industry_id, industry.partner, dry_run=dry_run, record=record, repos=repos
        )

    coverage: list[str] = []
    if industry_id and not dry_run:
        enabled = [
            source for source in await repos.sources.list_sources(industry_id) if source.enabled
        ]
        coverage = coverage_warnings(
            languages=sorted({source.language for source in enabled}),
            enabled_sources=len(enabled),
            trust_values=[source.trust for source in enabled],
        )

    counts = {"created": 0, "updated": 0, "skipped": 0}
    for action in actions:
        counts[action["action"]] += 1
    return {
        "slug": industry.slug,
        "state": state,
        "actions": actions,
        "counts": counts,
        "coverage": coverage,
    }


async def _apply_partner(
    industry_id: str | None,
    partner: PartnerProfile,
    *,
    dry_run: bool,
    record: Callable[[str, str, str], None],
    repos: Repositories,
) -> None:
    rows = await repos.catalog.list_partners(industry_id) if industry_id else []
    if not rows:
        record("partner", partner.name, "created")
        if not dry_run:
            if industry_id is None:  # pragma: no cover - created above
                raise ProfileError(f"industry '{partner.name}': industry row missing")
            await repos.catalog.create_partner(
                industry_id=industry_id,
                name=partner.name,
                contact_email=partner.contact_email,
                regions=partner.regions,
            )
            if abs(partner.weight - 1.0) > 0.001:
                created = await repos.catalog.list_partners(industry_id)
                if created:
                    await repos.catalog.update_partner(
                        str(created[0]["id"]), {"weight": partner.weight}
                    )
        return
    changes = _partner_changes(rows[0], partner)
    if changes:
        record("partner", partner.name, "updated")
        if not dry_run:
            await repos.catalog.update_partner(str(rows[0]["id"]), changes)
    else:
        record("partner", partner.name, "skipped")


def _channel_changes(
    channel: Any,
    industry: IndustryProfile,
    theme: dict[str, Any],
    disclaimers: dict[str, str],
) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    if channel.base_name != industry.name:
        changes["name"] = industry.name
    if channel.theme != theme:
        changes["theme"] = theme
    if channel.disclaimers != disclaimers:
        changes["disclaimers"] = disclaimers
    if as_dict(channel.cta) != as_dict(industry.cta):
        changes["cta"] = industry.cta
    if channel.timezone != industry.timezone:
        changes["timezone"] = industry.timezone
    if channel.retention_days != industry.retention_days:
        changes["retention_days"] = industry.retention_days
    if channel.sort_order != industry.sort_order:
        changes["sort_order"] = industry.sort_order
    if channel.enabled != industry.enabled:
        changes["enabled"] = industry.enabled
    return changes


def _topic_changes(row: dict[str, Any], topic: TopicProfile) -> bool:
    return (
        as_dict(row.get("label")) != topic.label
        or as_dict(row.get("keywords")) != topic.keywords
        or abs(float(row["weight"]) - topic.weight) > 0.001
    )


def _source_changes(found: Any, source: SourceProfile, url: str) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    if found.feed_url != url:
        changes["feed_url"] = url
    if found.name != source.name:
        changes["name"] = source.name
    if found.language != source.language:
        changes["language"] = source.language
    if abs(found.trust - source.trust) > 0.001:
        changes["trust"] = source.trust
    if found.enabled != source.enabled:
        changes["enabled"] = source.enabled
    if found.allow_http != source.allow_http:
        changes["allow_http"] = source.allow_http
    if found.poll_interval_min != source.poll_interval_min:
        changes["poll_interval_min"] = source.poll_interval_min
    if (found.terms_url or None) != (source.terms_url or None):
        changes["terms_url"] = source.terms_url
    return changes


def _partner_changes(existing: dict[str, Any], partner: PartnerProfile) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    if existing.get("name") != partner.name:
        changes["name"] = partner.name
    if existing.get("contact_email") != partner.contact_email:
        changes["contact_email"] = partner.contact_email
    if abs(float(existing.get("weight") or 0) - partner.weight) > 0.001:
        changes["weight"] = partner.weight
    if list(existing.get("regions") or []) != partner.regions:
        changes["regions"] = partner.regions
    return changes
