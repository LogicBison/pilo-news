"""Optional SMTP notifications. Missing configuration is a no-op, never a failure."""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

import structlog

from news_api.platform.settings import get_settings

log = structlog.get_logger(__name__)


def _send(message: EmailMessage) -> None:
    settings = get_settings()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        smtp.ehlo()
        if settings.smtp_port != 25:
            smtp.starttls()
            smtp.ehlo()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)


async def _deliver(message: EmailMessage, event: str) -> bool:
    settings = get_settings()
    if not settings.smtp_host:
        log.info("notify.skipped", action=event, reason="smtp_not_configured")
        return False
    try:
        await asyncio.to_thread(_send, message)
        log.info("notify.sent", action=event)
        return True
    except Exception as exc:
        log.warning("notify.failed", action=event, error=type(exc).__name__)
        return False


def _message(to: str, subject: str, body: str) -> EmailMessage:
    settings = get_settings()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_user or settings.contact_to
    message["To"] = to
    message.set_content(body)
    return message


async def notify_lead(
    partner_email: str,
    *,
    industry: str,
    kind: str,
    name: str,
    email: str,
    phone: str | None,
    company: str | None,
    message: str | None,
) -> bool:
    body = (
        f"New {kind} request for {industry}.\n\n"
        f"Name: {name}\nEmail: {email}\nPhone: {phone or '-'}\nCompany: {company or '-'}\n\n"
        f"Message:\n{message or '-'}\n\n"
        "Reply within the 24-hour partner SLA. Do not forward this message."
    )
    return await _deliver(
        _message(partner_email, f"System News lead: {industry}", body), "lead.routed"
    )


async def notify_contact(
    *, industry: str | None, name: str, email: str, phone: str | None, message: str
) -> bool:
    settings = get_settings()
    body = (
        f"Contact message for {industry or 'the desk'}.\n\n"
        f"Name: {name}\nEmail: {email}\nPhone: {phone or '-'}\n\n{message}"
    )
    return await _deliver(
        _message(settings.contact_to, f"System News contact: {industry or 'desk'}", body),
        "contact.received",
    )
