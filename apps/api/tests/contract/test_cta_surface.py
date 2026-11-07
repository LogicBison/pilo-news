"""Funnel events from the apex lobby carry no industry, only a surface.

The lobby is cross-desk: binding its events to one channel would fake attribution
that the read-out then reports as real.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_surface_event_is_accepted_without_an_industry(client) -> None:
    response = await client.post(
        "/v1/cta-events",
        json={
            "surface": "lobby",
            "event": "cta_click",
            "placement": "lobby-services",
            "locale": "en",
            "session_hash": "surface-test",
        },
    )
    assert response.status_code == 204, response.text


@pytest.mark.asyncio
async def test_event_needs_either_an_industry_or_a_surface(client) -> None:
    response = await client.post(
        "/v1/cta-events", json={"event": "cta_click", "placement": "nowhere"}
    )
    assert response.status_code == 422
    assert "surface" in response.text


@pytest.mark.asyncio
async def test_unknown_industry_is_still_rejected(client) -> None:
    response = await client.post(
        "/v1/cta-events", json={"industry": "no-such-desk", "event": "cta_click"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_desk_enter_is_a_known_event(client) -> None:
    response = await client.post(
        "/v1/cta-events",
        json={"industry": "legal", "event": "desk_enter", "placement": "lobby-desk"},
    )
    assert response.status_code == 204, response.text


@pytest.mark.asyncio
async def test_funnel_separates_lobby_events_from_channel_events(admin_client, client) -> None:
    await client.post(
        "/v1/cta-events",
        json={"surface": "lobby", "event": "cta_impression", "placement": "lobby-services"},
    )
    await client.post(
        "/v1/cta-events",
        json={"industry": "legal", "event": "desk_enter", "placement": "lobby-desk"},
    )

    response = await admin_client.get("/v1/admin/funnel?days=30")
    assert response.status_code == 200
    rows = response.json()["channels"]
    lobby = [row for row in rows if row.get("surface") == "lobby"]
    assert lobby, rows
    assert lobby[0]["industry"] == ""
    assert lobby[0]["events"]["cta_impression"] >= 1
    channel_rows = [row for row in rows if row["industry"] == "legal"]
    assert channel_rows
    assert channel_rows[0]["surface"] == ""
    assert channel_rows[0]["events"]["desk_enter"] >= 1
