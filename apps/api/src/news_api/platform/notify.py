"""Optional SMTP notifications. Missing configuration is a no-op, never a failure.

The deployment picks *where* it hands off mail with ``SMTP_TRANSPORT``; the
sender, the message and the failure discipline are identical on every lane
(see ``SmtpConfig.from_settings``). A lane that is selected but has no host or
no sender is not an error - the deployment is in-app-only and the caller logs
``notify.skipped``.
"""

from __future__ import annotations

import asyncio
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

import structlog

from news_api.platform.settings import Settings, get_settings

log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class SmtpConfig:
    """One deployment's resolved SMTP lane."""

    host: str = ""
    port: int = 587
    user: str = ""
    password: str = ""
    sender: str = ""
    starttls: bool = True
    use_ssl: bool = False
    timeout_seconds: float = 10.0
    #: ``gateway`` / ``direct`` when a lane was selected, else ``""`` (flat).
    transport: str = ""

    @property
    def configured(self) -> bool:
        """A relay needs a host and a sender; without them there is nothing to send."""
        return bool(self.host.strip() and self.sender.strip())

    @classmethod
    def from_settings(cls, settings: Settings) -> SmtpConfig:
        """Resolve the endpoint from the selected lane.

        ``gateway`` and ``direct`` swap **only** the endpoint. The sender is
        ``SMTP_FROM`` on every lane; when it is unset the flat lane falls back
        to ``SMTP_USER`` (the historical behaviour), while a selected lane
        would otherwise send from its relay login - which is why the env files
        always set ``SMTP_FROM``.
        """
        transport = settings.smtp_transport
        if transport == "gateway":
            host, port = settings.smtp_gateway_host, settings.smtp_gateway_port
            user, password = settings.smtp_gateway_user, settings.smtp_gateway_password
            use_ssl = settings.smtp_gateway_ssl
        elif transport == "direct":
            host, port = settings.smtp_direct_host, settings.smtp_direct_port
            user, password = settings.smtp_direct_user, settings.smtp_direct_password
            use_ssl = settings.smtp_direct_ssl
        else:
            host, port = settings.smtp_host, settings.smtp_port
            user, password = settings.smtp_user, settings.smtp_password
            use_ssl = settings.smtp_ssl
        return cls(
            host=host.strip(),
            port=port,
            user=user.strip(),
            password=password,
            sender=settings.smtp_from.strip() or user.strip(),
            starttls=settings.smtp_starttls,
            use_ssl=use_ssl,
            timeout_seconds=settings.smtp_timeout_seconds,
            transport=transport,
        )


def _connect(config: SmtpConfig) -> smtplib.SMTP:
    if config.use_ssl:
        return smtplib.SMTP_SSL(
            config.host,
            config.port,
            timeout=config.timeout_seconds,
            context=ssl.create_default_context(),
        )
    return smtplib.SMTP(config.host, config.port, timeout=config.timeout_seconds)


def _send(message: EmailMessage, config: SmtpConfig) -> None:
    with _connect(config) as smtp:
        if config.starttls and not config.use_ssl:
            # Verified context: no upgrade, no credentials in the clear.
            smtp.starttls(context=ssl.create_default_context())
        if config.user:
            smtp.login(config.user, config.password)
        smtp.send_message(message)


async def _deliver(config: SmtpConfig, message: EmailMessage, event: str) -> bool:
    if not config.configured:
        log.info(
            "notify.skipped",
            action=event,
            transport=config.transport or "flat",
            reason="smtp_not_configured",
        )
        return False
    try:
        await asyncio.to_thread(_send, message, config)
        log.info("notify.sent", action=event, transport=config.transport or "flat")
        return True
    except Exception as exc:
        log.warning(
            "notify.failed",
            action=event,
            transport=config.transport or "flat",
            error=type(exc).__name__,
        )
        return False


def _compose(
    config: SmtpConfig, to: str, subject: str, body: str, *, reply_to: str | None = None
) -> EmailMessage:
    message = EmailMessage()
    sender_domain = config.sender.rsplit("@", 1)[-1].strip("> ") or "localhost"
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = make_msgid(domain=sender_domain)
    message["Subject"] = subject
    message["From"] = config.sender
    message["To"] = to
    if reply_to:
        # The sender domain is send-only (Brevo return-path MX), so a reply to
        # the From address would vanish. Point it at the person who wrote in.
        message["Reply-To"] = reply_to
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
    config = SmtpConfig.from_settings(get_settings())
    body = (
        f"New {kind} request for {industry}.\n\n"
        f"Name: {name}\nEmail: {email}\nPhone: {phone or '-'}\nCompany: {company or '-'}\n\n"
        f"Message:\n{message or '-'}\n\n"
        "Reply within the 24-hour partner SLA. Do not forward this message."
    )
    return await _deliver(
        config,
        _compose(
            config,
            partner_email,
            f"System News lead: {industry}",
            body,
            reply_to=email,
        ),
        "lead.routed",
    )


async def notify_contact(
    *, industry: str | None, name: str, email: str, phone: str | None, message: str
) -> bool:
    settings = get_settings()
    config = SmtpConfig.from_settings(settings)
    body = (
        f"Contact message for {industry or 'the desk'}.\n\n"
        f"Name: {name}\nEmail: {email}\nPhone: {phone or '-'}\n\n{message}"
    )
    return await _deliver(
        config,
        _compose(
            config,
            settings.contact_to,
            f"System News contact: {industry or 'desk'}",
            body,
            reply_to=email,
        ),
        "contact.received",
    )
