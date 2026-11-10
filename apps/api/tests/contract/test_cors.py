"""Third-party pages read the public API straight from the browser.

A missing `Access-Control-Allow-Origin` on the actual GET (not just the
preflight) silently breaks every embeddable integration, so it is pinned here.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_public_read_grants_any_origin(client) -> None:
    response = await client.get("/v1/industries")
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
    assert "ETag" in response.headers["access-control-expose-headers"]


@pytest.mark.asyncio
async def test_preflight_is_answered_without_auth(client) -> None:
    response = await client.options(
        "/v1/news",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 204
    assert response.headers["access-control-allow-origin"] == "*"
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "If-None-Match" in response.headers["access-control-allow-headers"]


@pytest.mark.asyncio
async def test_admin_surface_grants_no_cors(client) -> None:
    response = await client.get("/v1/admin/sources?industry=legal")
    assert "access-control-allow-origin" not in response.headers
