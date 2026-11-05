from __future__ import annotations

from news_api.platform.errors import InvalidLocale

SUPPORTED_LOCALES: tuple[str, ...] = ("en", "es")
DEFAULT_LOCALE = "en"


def normalize_locale(value: str | None) -> str:
    """Normalize a BCP 47 tag to a supported base language or raise InvalidLocale."""
    if not value:
        return DEFAULT_LOCALE
    base = value.strip().lower().replace("_", "-").split("-")[0]
    if base not in SUPPORTED_LOCALES:
        raise InvalidLocale(f"Unsupported locale '{value}'. Supported: en, es.")
    return base


def parse_accept_language(header: str | None) -> str | None:
    if not header:
        return None
    candidates: list[tuple[float, int, str]] = []
    for index, part in enumerate(header.split(",")):
        token = part.strip()
        if not token:
            continue
        tag, _, params = token.partition(";")
        quality = 1.0
        for param in params.split(";"):
            key, _, raw = param.strip().partition("=")
            if key == "q":
                try:
                    quality = float(raw)
                except ValueError:
                    quality = 0.0
        base = tag.strip().lower().replace("_", "-").split("-")[0]
        if base in SUPPORTED_LOCALES:
            candidates.append((quality, -index, base))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][2]


def negotiate_locale(explicit: str | None, accept_language: str | None, cookie: str | None) -> str:
    if explicit:
        return normalize_locale(explicit)
    if cookie:
        try:
            return normalize_locale(cookie)
        except InvalidLocale:
            pass
    return parse_accept_language(accept_language) or DEFAULT_LOCALE
