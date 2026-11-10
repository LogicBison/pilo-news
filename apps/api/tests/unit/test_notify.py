from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from news_api.platform import notify
from news_api.platform.settings import Settings

GATEWAY = {
    "smtp_transport": "gateway",
    "smtp_from": "HeraldFox <info@em.heraldfox.com>",
    "smtp_gateway_host": "smtp.iterwire.com",
    "smtp_gateway_port": 2525,
    "smtp_gateway_user": "heraldfox@relay.iterwire.com",
    "smtp_gateway_password": "secret",
    "smtp_gateway_ssl": False,
}


def _config(**overrides: Any) -> notify.SmtpConfig:
    return notify.SmtpConfig.from_settings(Settings(**{**GATEWAY, **overrides}))


def test_gateway_lane_resolves_its_endpoint_and_sender() -> None:
    config = _config()

    assert config.host == "smtp.iterwire.com"
    assert config.port == 2525
    assert config.user == "heraldfox@relay.iterwire.com"
    assert config.password == "secret"
    assert config.sender == "HeraldFox <info@em.heraldfox.com>"
    assert config.use_ssl is False
    assert config.starttls is True
    assert config.transport == "gateway"


def test_direct_lane_uses_implicit_tls() -> None:
    config = _config(
        smtp_transport="direct",
        smtp_direct_host="mail.iterwire.com",
        smtp_direct_port=465,
        smtp_direct_user="info@em.heraldfox.com",
        smtp_direct_password="secret",
        smtp_direct_ssl=True,
    )

    assert config.host == "mail.iterwire.com"
    assert config.port == 465
    assert config.user == "info@em.heraldfox.com"
    assert config.use_ssl is True
    assert config.transport == "direct"


def test_flat_lane_keeps_the_historical_block() -> None:
    config = _config(
        smtp_transport="",
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="mailer@example.com",
        smtp_password="secret",
        smtp_from="",
    )

    assert config.host == "smtp.example.com"
    assert config.user == "mailer@example.com"
    assert config.sender == "mailer@example.com"
    assert config.transport == ""


def test_smtp_from_wins_over_the_login() -> None:
    config = _config(smtp_gateway_user="relay@relay.iterwire.com")

    assert config.user == "relay@relay.iterwire.com"
    assert config.sender == "HeraldFox <info@em.heraldfox.com>"


def test_transport_is_normalised() -> None:
    assert _config(smtp_transport=" Gateway ").transport == "gateway"


def test_unknown_transport_fails_at_startup() -> None:
    with pytest.raises(ValidationError):
        _config(smtp_transport="gatewat")


def test_a_lane_without_a_host_or_sender_is_not_configured() -> None:
    assert _config(smtp_gateway_host="").configured is False
    assert _config(smtp_from="", smtp_gateway_user="").configured is False
    assert _config().configured is True


def test_compose_sets_the_configured_sender_and_recipient() -> None:
    config = _config()
    message = notify._compose(
        config, "news@heraldfox.com", "subject", "body", reply_to="lead@example.com"
    )

    assert message["From"] == "HeraldFox <info@em.heraldfox.com>"
    assert message["To"] == "news@heraldfox.com"
    assert message["Reply-To"] == "lead@example.com"
    assert message["Subject"] == "subject"
    assert message["Date"]
    assert message["Message-ID"].endswith("@em.heraldfox.com>")
    assert message.get_content().strip() == "body"


def test_compose_leaves_reply_to_unset_without_a_contact() -> None:
    message = notify._compose(_config(), "news@heraldfox.com", "subject", "body")

    assert message["Reply-To"] is None


class _Recorder:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    def __enter__(self) -> _Recorder:
        return self

    def __exit__(self, *exc: object) -> None:
        self.calls.append(("quit",))

    def starttls(self, *, context: object | None = None) -> None:
        self.calls.append(("starttls", context is not None))

    def login(self, user: str, password: str) -> None:
        self.calls.append(("login", user, password))

    def send_message(self, message: object) -> None:
        self.calls.append(("send",))


@pytest.mark.parametrize(
    ("use_ssl", "starttls", "expected"),
    [
        (False, True, [("starttls", True), ("login", "u", "p"), ("send",), ("quit",)]),
        (True, True, [("login", "u", "p"), ("send",), ("quit",)]),
    ],
)
def test_send_negotiates_tls_before_authenticating(
    monkeypatch: pytest.MonkeyPatch,
    use_ssl: bool,
    starttls: bool,
    expected: list[tuple[Any, ...]],
) -> None:
    recorder = _Recorder()
    monkeypatch.setattr(notify, "_connect", lambda config: recorder)
    config = notify.SmtpConfig(
        host="smtp.example.com", user="u", password="p", use_ssl=use_ssl, starttls=starttls
    )

    notify._send(notify._compose(config, "to@example.com", "s", "b"), config)

    assert recorder.calls == expected


async def test_deliver_skips_when_the_lane_is_unconfigured() -> None:
    config = notify.SmtpConfig(host="", sender="")
    message = notify._compose(config, "to@example.com", "s", "b")

    assert await notify._deliver(config, message, "contact.received") is False
