from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from news_api.platform.clock import utcnow
from news_api.platform.settings import get_settings

API_KEY_PREFIX = "sn_live_"
_hasher = PasswordHasher()


def _pepper() -> str:
    return get_settings().secret_key


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_api_key(api_key: str) -> str:
    return sha256_hex(f"{_pepper()}:{api_key}")


def generate_api_key() -> tuple[str, str, str]:
    """Return (plaintext, hash, prefix). Plaintext is shown once and never stored."""
    plaintext = f"{API_KEY_PREFIX}{secrets.token_hex(32)}"
    return plaintext, hash_api_key(plaintext), plaintext[:16]


def constant_eq(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def hash_personal(value: str) -> str:
    """Peppered hash for IP/UA-derived values; never store raw network identifiers."""
    return sha256_hex(f"{_pepper()}:{value}")


def admin_auth_configured() -> bool:
    settings = get_settings()
    return bool(settings.admin_password_hash or settings.admin_password)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_admin_password(password: str) -> bool:
    settings = get_settings()
    if settings.admin_password_hash:
        try:
            return bool(_hasher.verify(settings.admin_password_hash, password))
        except (VerificationError, InvalidHashError):
            return False
    if settings.admin_password:
        return constant_eq(settings.admin_password, password)
    return False


def create_admin_token(subject: str, email: str, minutes: int | None = None) -> tuple[str, str]:
    settings = get_settings()
    ttl = minutes or settings.admin_session_minutes
    now = utcnow()
    jti = uuid.uuid4().hex
    payload: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "jti": jti,
        "type": "admin",
        "iat": now,
        "exp": now + timedelta(minutes=ttl),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token, jti


def decode_admin_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=["HS256"],
        options={"require": ["sub", "jti", "exp"]},
    )
    if payload.get("type") != "admin":
        raise jwt.InvalidTokenError("wrong token type")
    return payload


def new_csrf_token() -> str:
    return secrets.token_urlsafe(24)


def bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()
