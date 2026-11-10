from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

import httpx

from news_api.articles.infrastructure.fetcher import validate_fetch_url
from news_api.articles.infrastructure.politeness import USER_AGENT

MAX_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 3
TIMEOUT = httpx.Timeout(30.0, connect=10.0)


async def fetch_json(url: str, *, params: Any = None) -> dict[str, Any]:
    # httpx accepts repeated query keys as a list of tuples; the caller owns the
    # shape because Federal Register uses bracketed condition keys.
    current = url
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False) as client:
        for attempt in range(MAX_REDIRECTS + 1):
            await validate_fetch_url(current)
            async with client.stream(
                "GET",
                current,
                params=params if attempt == 0 else None,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            ) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        raise ValueError("source redirect without a location")
                    current = urljoin(current, location)
                    continue
                if response.status_code >= 400:
                    raise ValueError(f"source returned http {response.status_code}")
                chunks: list[bytes] = []
                total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ValueError("source response too large")
                    chunks.append(chunk)
                payload = json.loads(b"".join(chunks))
                if not isinstance(payload, dict):
                    raise ValueError("source returned a non-object payload")
                return payload
    raise ValueError("source redirected too many times")
