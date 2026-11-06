from __future__ import annotations

import json
import re
from typing import Any

import structlog
from sqlalchemy import text

from news_api.channels.domain.theme import Channel
from news_api.platform.clock import utcnow
from news_api.platform.db import fetch_one, session_scope
from news_api.platform.errors import ValidationProblem
from news_api.platform.metrics import LEAD_ROUTE_LATENCY, LEADS
from news_api.platform.notify import notify_lead
from news_api.platform.security import hash_personal

log = structlog.get_logger(__name__)

CONSENT_VERSION = "2026-11-05-v1"
# Throwaway mailboxes never reach a partner; rejecting them keeps CPL honest.
DISPOSABLE_DOMAINS = frozenset(
    {
        "mailinator.com",
        "guerrillamail.com",
        "10minutemail.com",
        "tempmail.com",
        "temp-mail.org",
        "yopmail.com",
        "trashmail.com",
        "sharklasers.com",
        "getnada.com",
        "dispostable.com",
    }
)
SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\d[ -]?){13,19}\b"),
)


def reject_sensitive(payload: dict[str, Any]) -> None:
    haystack = " ".join(str(payload.get(key) or "") for key in ("message", "company", "name"))
    if any(pattern.search(haystack) for pattern in SENSITIVE_PATTERNS):
        raise ValidationProblem(
            "Please do not include Social Security, card, or account numbers in this form."
        )


async def partner_for(industry_id: str) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT id, name, contact_email FROM partners
        WHERE industry_id = CAST(:industry_id AS uuid) AND status = 'active'
        ORDER BY weight DESC LIMIT 1
        """,
        {"industry_id": industry_id},
    )


async def duplicate_lead(industry_id: str, email: str, minutes: int = 10) -> dict[str, Any] | None:
    return await fetch_one(
        """
        SELECT id FROM leads
        WHERE industry_id = CAST(:industry_id AS uuid)
          AND lower(email) = lower(:email)
          AND created_at >= now() - make_interval(mins => :minutes)
        ORDER BY created_at DESC LIMIT 1
        """,
        {"industry_id": industry_id, "email": email, "minutes": minutes},
    )


def qualification_options(channel: Channel) -> dict[str, Any]:
    """Channel CTA may carry a `qualify` block: label, required, options."""
    cta = channel.cta if isinstance(channel.cta, dict) else {}
    config = cta.get("qualify")
    return config if isinstance(config, dict) else {}


def check_qualification(channel: Channel, payload: dict[str, Any]) -> str | None:
    """Return the validated qualification value, or raise on a missing/invalid one."""
    config = qualification_options(channel)
    if not config:
        return payload.get("qualification")
    allowed = {
        str(option.get("value"))
        for option in config.get("options") or []
        if isinstance(option, dict) and option.get("value")
    }
    value = payload.get("qualification")
    if value is None or str(value).strip() == "":
        # The brief rung is deliberately two fields; a missing answer is only a
        # problem on the consultation form, where the partner needs the context.
        if config.get("required") and payload.get("kind") not in {"brief", "question", "asset"}:
            raise ValidationProblem("Choose the option that fits your request.")
        return None
    value = str(value)
    if allowed and value not in allowed:
        raise ValidationProblem("Choose an option from the list.")
    return value


async def create_lead(
    channel: Channel,
    payload: dict[str, Any],
    *,
    ip_hash: str,
    ua_hash: str,
) -> tuple[str, bool, str | None]:
    """Create or silently de-duplicate a lead. Returns (id, duplicate, partner_name)."""
    if not payload.get("consent"):
        raise ValidationProblem("Consent is required to submit this form.")
    reject_sensitive(payload)
    domain = str(payload["email"]).rsplit("@", 1)[-1].lower()
    if domain in DISPOSABLE_DOMAINS:
        raise ValidationProblem("Use a permanent email address - this one looks temporary.")
    if channel.slug == "logistics" and payload.get("kind") in {"consultation", "question"}:
        if not payload.get("phone"):
            raise ValidationProblem("A phone number is required for logistics inquiries.")
        if not payload.get("company"):
            raise ValidationProblem("A company is required for logistics inquiries.")
    qualification = check_qualification(channel, payload)

    existing = await duplicate_lead(channel.id, str(payload["email"]))
    partner = await partner_for(channel.id)
    if existing:
        return str(existing["id"]), True, str(partner["name"]) if partner else None

    article_id = payload.get("article_id")
    if article_id:
        found = await fetch_one(
            """
            SELECT id FROM articles
            WHERE id = CAST(:id AS uuid) AND industry_id = CAST(:industry_id AS uuid)
            """,
            {"id": article_id, "industry_id": channel.id},
        )
        if not found:
            raise ValidationProblem("The referenced article does not belong to this channel.")
        article_id = str(found["id"])

    now = utcnow()
    partner_id = str(partner["id"]) if partner else None
    partner_name = str(partner["name"]) if partner else None
    status = "routed" if partner_id else "new"
    utm = payload.get("utm") or {}
    if not isinstance(utm, dict):
        utm = {}

    async with session_scope() as session:
        row = await session.execute(
            text(
                """
                INSERT INTO leads (
                    industry_id, partner_id, kind, name, email, phone, company, message,
                    qualification, asset, locale, source_page, article_id, utm, consent_version,
                    consent_at, ip_hash, ua_hash, status
                ) VALUES (
                    CAST(:industry_id AS uuid), CAST(:partner_id AS uuid), :kind, :name, :email,
                    :phone, :company, :message, :qualification, :asset, :locale, :source_page,
                    CAST(:article_id AS uuid), CAST(:utm AS jsonb), :consent_version,
                    :consent_at, :ip_hash, :ua_hash, :status
                ) RETURNING id
                """
            ),
            {
                "industry_id": channel.id,
                "partner_id": partner_id,
                "kind": payload["kind"],
                "name": payload["name"],
                "email": payload["email"],
                "phone": payload.get("phone"),
                "company": payload.get("company"),
                "message": payload.get("message"),
                "qualification": qualification,
                "asset": payload.get("asset"),
                "locale": payload.get("locale") or "en",
                "source_page": payload.get("source_page"),
                "article_id": article_id,
                "utm": json.dumps(utm),
                "consent_version": CONSENT_VERSION,
                "consent_at": now,
                "ip_hash": ip_hash,
                "ua_hash": ua_hash,
                "status": status,
            },
        )
        lead_id = str(row.scalar_one())
        await session.execute(
            text(
                """
                INSERT INTO lead_events (lead_id, actor, action, payload)
                VALUES (CAST(:lead_id AS uuid), 'public', 'created', CAST(:payload AS jsonb))
                """
            ),
            {
                "lead_id": lead_id,
                "payload": json.dumps(
                    {
                        "kind": payload["kind"],
                        "status": status,
                        "consent_version": CONSENT_VERSION,
                        "partner_id": partner_id,
                    }
                ),
            },
        )
        if partner_id:
            await session.execute(
                text(
                    """
                    INSERT INTO lead_events (lead_id, actor, action, payload)
                    VALUES (CAST(:lead_id AS uuid), 'system', 'routed', CAST(:payload AS jsonb))
                    """
                ),
                {
                    "lead_id": lead_id,
                    "payload": json.dumps({"partner_id": partner_id, "partner": partner_name}),
                },
            )

    LEADS.labels(industry=channel.slug, status=status).inc()
    if partner_id:
        LEAD_ROUTE_LATENCY.labels(industry=channel.slug).observe(0.0)
        await notify_lead(
            str(partner["contact_email"]) if partner else "",
            industry=channel.slug,
            kind=str(payload["kind"]),
            name=str(payload["name"]),
            email=str(payload["email"]),
            phone=payload.get("phone"),
            company=payload.get("company"),
            message=payload.get("message"),
        )
    log.info(
        "lead.created",
        industry=channel.slug,
        lead_id=lead_id,
        kind=payload["kind"],
        status=status,
        partner=bool(partner_id),
    )
    return lead_id, False, str(partner["name"]) if partner else None


def lead_public_response(lead_id: str, duplicate: bool) -> dict[str, Any]:
    if duplicate:
        return {"status": "received"}
    return {"id": lead_id}


def ip_and_ua_hash(ip: str, user_agent: str) -> tuple[str, str]:
    return hash_personal(ip), hash_personal(user_agent[:400])
