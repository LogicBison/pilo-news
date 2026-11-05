from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass
from datetime import UTC, datetime

from news_api.platform.errors import InvalidCursor


@dataclass(frozen=True)
class Cursor:
    score: float
    published_at: datetime
    article_id: str


def encode_cursor(score: float, published_at: datetime, article_id: str) -> str:
    payload = {
        "v": 1,
        "s": round(float(score), 6),
        "p": published_at.astimezone(UTC).isoformat(),
        "i": str(article_id),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(value: str | None) -> Cursor | None:
    if not value:
        return None
    if len(value) > 512:
        raise InvalidCursor("Cursor is too long.")
    padded = value + "=" * (-len(value) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        payload = json.loads(raw)
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise InvalidCursor("Cursor is malformed.") from exc
    if not isinstance(payload, dict) or payload.get("v") != 1:
        raise InvalidCursor("Unsupported cursor version.")
    try:
        score = float(payload["s"])
        published_at = datetime.fromisoformat(str(payload["p"]))
        article_id = str(payload["i"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidCursor("Cursor is malformed.") from exc
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=UTC)
    return Cursor(score=score, published_at=published_at, article_id=article_id)
