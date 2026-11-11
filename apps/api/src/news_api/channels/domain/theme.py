from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from news_api.channels.domain.offers import resolve_offers
from news_api.platform.jsons import as_dict

REQUIRED_TOKENS = (
    "primary",
    "accent",
    "bg",
    "surface",
    "text",
    "muted",
    "border",
    "radius",
    "font_heading",
    "font_body",
    "layout",
)
LAYOUT_VARIANTS = ("editorial", "professional", "academic")

RESERVED_SLUGS = frozenset(
    {
        "en",
        "es",
        "api",
        "admin",
        "v1",
        "health",
        "static",
        "sitemap.xml",
        "robots.txt",
        "_next",
        # Apex routes: a channel slug must never shadow the lobby, the services
        # page or the network's legal pages (ADR 015 / lobby plan §7 R3).
        "services",
        "pricing",
        "privacy",
        "terms",
    }
)


def is_reserved_slug(slug: str) -> bool:
    return slug in RESERVED_SLUGS


def _channel(value: int) -> float:
    normalized = value / 255
    return normalized / 12.92 if normalized <= 0.03928 else ((normalized + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    color = hex_color.lstrip("#")
    if len(color) != 6:
        raise ValueError(f"invalid color {hex_color!r}")
    r, g, b = (int(color[index : index + 2], 16) for index in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(foreground: str, background: str) -> float:
    first = relative_luminance(foreground)
    second = relative_luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def validate_theme(theme: dict[str, Any]) -> list[str]:
    """Return a list of human-readable problems; empty means the theme is valid."""
    problems: list[str] = []
    missing = [token for token in REQUIRED_TOKENS if not theme.get(token)]
    if missing:
        problems.append(f"missing tokens: {', '.join(missing)}")
        return problems
    for token in ("primary", "accent", "bg", "surface", "text", "muted", "border"):
        value = str(theme[token])
        if not (value.startswith("#") and len(value) == 7):
            problems.append(f"{token} must be a 6-digit hex color")
    if problems:
        return problems
    if str(theme["layout"]) not in LAYOUT_VARIANTS:
        problems.append(f"layout must be one of {', '.join(LAYOUT_VARIANTS)}")
    checks = [
        ("text on background", "text", "bg", 4.5),
        ("muted text on background", "muted", "bg", 4.5),
        ("white on primary", "#ffffff", "primary", 4.5),
        ("accent on background", "accent", "bg", 3.0),
        ("text on surface", "text", "surface", 4.5),
    ]
    for label, fg, bg, minimum in checks:
        foreground = "#ffffff" if fg == "#ffffff" else str(theme[fg])
        background = str(theme[bg])
        try:
            ratio = contrast_ratio(foreground, background)
        except ValueError:
            problems.append(f"{label}: invalid color")
            continue
        if ratio < minimum:
            problems.append(f"{label}: contrast {ratio:.2f} < {minimum}")
    fonts = {str(theme["font_heading"]), str(theme["font_body"])}
    if len(fonts) > 2:
        problems.append("at most two font families")
    return problems


@dataclass(frozen=True)
class Channel:
    id: str
    slug: str
    code: str
    name: str
    base_name: str
    tagline: str
    theme: dict[str, Any]
    locales: list[str]
    disclaimers: dict[str, str]
    cta: dict[str, Any]
    timezone: str
    retention_days: int
    enabled: bool
    sort_order: int = 0
    fetch_interval_minutes: int | None = None
    auto_fetch_enabled: bool = True
    ai_summaries_enabled: bool = True
    offers: dict[str, Any] = field(default_factory=dict)

    @property
    def effective_offers(self) -> dict[str, bool]:
        return resolve_offers(self.cta, self.offers)

    def effective_fetch_interval(self, default_minutes: int) -> int:
        return self.fetch_interval_minutes or default_minutes

    @property
    def theme_summary(self) -> dict[str, Any]:
        return {
            "primary": self.theme.get("primary"),
            "accent": self.theme.get("accent"),
            "layout": self.theme.get("layout"),
        }

    @property
    def default_theme(self) -> dict[str, Any]:
        return self.theme

    def disclaimer(self, locale: str) -> str:
        return self.disclaimers.get(locale) or self.disclaimers.get("en", "")


def channel_from_row(row: dict[str, Any]) -> Channel:
    return Channel(
        id=str(row["id"]),
        slug=str(row["slug"]),
        code=str(row["code"]),
        name=str(row.get("display_name") or row["name"]),
        base_name=str(row["name"]),
        tagline=str(row.get("tagline") or ""),
        theme=as_dict(row.get("theme")),
        locales=list(row.get("locales") or ["en"]),
        disclaimers=as_dict(row.get("disclaimers")),
        cta=as_dict(row.get("cta")),
        timezone=str(row.get("timezone") or "America/El_Salvador"),
        retention_days=int(row.get("retention_days") or 7),
        enabled=bool(row.get("enabled", True)),
        sort_order=int(row.get("sort_order") or 0),
        fetch_interval_minutes=(
            int(row["fetch_interval_minutes"])
            if row.get("fetch_interval_minutes") is not None
            else None
        ),
        auto_fetch_enabled=bool(row.get("auto_fetch_enabled", True)),
        ai_summaries_enabled=bool(row.get("ai_summaries_enabled", True)),
        offers=as_dict(row.get("offers")),
    )


DEFAULT_THEMES: dict[str, dict[str, Any]] = {
    "editorial": {
        "primary": "#1e3a5f",
        "accent": "#8a4b08",
        "bg": "#ffffff",
        "surface": "#f6f7f9",
        "text": "#111827",
        "muted": "#4b5563",
        "border": "#d8dee6",
        "radius": "10px",
        "font_heading": "Georgia, Times New Roman, serif",
        "font_body": "system-ui, -apple-system, Segoe UI, sans-serif",
        "layout": "editorial",
    },
    "professional": {
        "primary": "#0b4f6c",
        "accent": "#0f766e",
        "bg": "#ffffff",
        "surface": "#f1f5f9",
        "text": "#0f172a",
        "muted": "#475569",
        "border": "#cbd5e1",
        "radius": "6px",
        "font_heading": "Arial, Helvetica, sans-serif",
        "font_body": "system-ui, -apple-system, Segoe UI, sans-serif",
        "layout": "professional",
    },
    "academic": {
        "primary": "#1d4ed8",
        "accent": "#b45309",
        "bg": "#fffdf7",
        "surface": "#f8fafc",
        "text": "#1f2937",
        "muted": "#4b5563",
        "border": "#dbe4f0",
        "radius": "10px",
        "font_heading": "Georgia, Times New Roman, serif",
        "font_body": "system-ui, -apple-system, Segoe UI, sans-serif",
        "layout": "academic",
    },
}


@dataclass(frozen=True)
class PublicChannel:
    slug: str
    name: str
    code: str
    locales: list[str]
    theme_summary: dict[str, Any]
    tagline: str = ""
    disclaimer: str = ""
    theme: dict[str, Any] = field(default_factory=dict)
    cta: dict[str, Any] = field(default_factory=dict)
    timezone: str = "America/El_Salvador"
