import pytest

from news_api.platform.clock import utcnow
from news_api.platform.errors import InvalidCursor
from news_api.platform.pagination import decode_cursor, encode_cursor
from news_api.platform.security import (
    create_admin_token,
    decode_admin_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_admin_password,
)


def test_cursor_round_trip() -> None:
    now = utcnow()
    token = encode_cursor(1.25, now, "00000000-0000-0000-0000-000000000001")
    cursor = decode_cursor(token)
    assert cursor is not None
    assert cursor.score == 1.25
    assert cursor.article_id == "00000000-0000-0000-0000-000000000001"


def test_cursor_rejects_garbage() -> None:
    with pytest.raises(InvalidCursor):
        decode_cursor("not-a-cursor")
    with pytest.raises(InvalidCursor):
        decode_cursor("x" * 600)


def test_api_key_hash_is_deterministic_and_prefixed() -> None:
    plaintext, digest, prefix = generate_api_key()
    assert plaintext.startswith("sn_live_")
    assert prefix == plaintext[:16]
    assert hash_api_key(plaintext) == digest
    assert hash_api_key(plaintext) != hash_api_key(plaintext + "x")


def test_password_hash_verifies() -> None:
    digest = hash_password("correct horse battery staple")
    assert digest.startswith("$argon2")
    assert verify_admin_password("test-admin-password") is True
    assert verify_admin_password("wrong") is False


def test_admin_token_round_trip() -> None:
    token, jti = create_admin_token("operator", "admin@example.com")
    payload = decode_admin_token(token)
    assert payload["jti"] == jti
    assert payload["email"] == "admin@example.com"
    assert payload["type"] == "admin"
