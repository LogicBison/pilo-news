"""Deployment profile schema.

A profile is the declarative, single-file description of one deployment: brand
metadata plus every industry channel with its theme, locale copy, topics,
sources, and optional partner. It never carries secrets; runtime settings stay
in `.env.<env>`.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class LocaleProfile(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    tagline: str = Field(default="", max_length=240)


class TopicProfile(BaseModel):
    slug: str = Field(pattern="^[a-z0-9-]{2,40}$")
    label: dict[str, str] = Field(default_factory=dict)
    weight: float = Field(default=1.0, gt=0, le=10)
    keywords: dict[str, list[str]] = Field(default_factory=dict)


class SourceProfile(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    feed_url: str = Field(min_length=8, max_length=2048)
    language: str = Field(default="en", max_length=10)
    trust: float = Field(default=0.7, ge=0, le=1)
    enabled: bool = True
    allow_http: bool = False
    poll_interval_min: int = Field(default=720, ge=5, le=1440)
    terms_url: str | None = Field(default=None, max_length=2048)
    # Licensed feeds: the credential lives in the environment, and the profile
    # carries only the variable's name. `header` may also set a publisher-
    # requested User-Agent (auth_header_name=User-Agent).
    licence_type: Literal[
        "unknown",
        "public-domain",
        "cc-by",
        "cc-by-sa",
        "syndication",
        "licensed",
        "proprietary",
    ] = "unknown"
    auth_type: Literal["none", "header", "basic"] = "none"
    auth_header_name: str | None = Field(default=None, max_length=120)
    auth_secret_ref: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]{2,63}$")

    @model_validator(mode="after")
    def _auth_is_coherent(self) -> SourceProfile:
        if self.auth_type == "none":
            if self.auth_header_name or self.auth_secret_ref:
                raise ValueError("auth_type=none cannot carry a header or secret reference")
        else:
            if not self.auth_secret_ref:
                raise ValueError("auth_type requires auth_secret_ref")
            if self.auth_type == "basic" and self.auth_header_name:
                raise ValueError("basic auth does not take a header name")
        return self


class PartnerProfile(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    contact_email: str = Field(
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        max_length=254,
    )
    weight: float = Field(default=1.0, ge=0, le=10)
    regions: list[str] = Field(default_factory=list)


class IndustryProfile(BaseModel):
    slug: str = Field(pattern="^[a-z0-9-]{2,40}$")
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    theme: dict[str, Any] = Field(default_factory=dict)
    locales: dict[str, LocaleProfile] = Field(default_factory=dict)
    disclaimers: dict[str, str] = Field(default_factory=dict)
    cta: dict[str, Any] = Field(default_factory=dict)
    timezone: str = Field(default="America/El_Salvador", max_length=64)
    retention_days: int = Field(default=30, ge=1, le=90)
    sort_order: int = Field(default=100, ge=0, le=10000)
    enabled: bool = True
    topics: list[TopicProfile] = Field(default_factory=list)
    sources: list[SourceProfile] = Field(default_factory=list)
    partner: PartnerProfile | None = None

    @property
    def locale_names(self) -> dict[str, dict[str, str]]:
        return {
            locale: {"name": copy.name, "tagline": copy.tagline}
            for locale, copy in self.locales.items()
        }


class DeploymentProfile(BaseModel):
    brand: str = Field(min_length=1, max_length=120)
    site_url: str = Field(default="", max_length=2048)
    default_locale: str = Field(default="en", max_length=10)
    default_industry: str | None = Field(default=None, max_length=40)
    refresh_interval_minutes: int = Field(default=720, ge=5, le=1440)
    industries: list[IndustryProfile] = Field(min_length=1)

    @field_validator("industries")
    @classmethod
    def _unique_slugs(cls, value: list[IndustryProfile]) -> list[IndustryProfile]:
        seen: set[str] = set()
        for industry in value:
            if industry.slug in seen:
                raise ValueError(f"duplicate industry slug '{industry.slug}'")
            seen.add(industry.slug)
        return value
