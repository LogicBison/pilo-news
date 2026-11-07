from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_desks_returns_the_lobby_shape(client) -> None:
    """One round trip for the apex lobby: every desk with address data iff live."""
    response = await client.get("/v1/desks")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["meta"]["locale"] == "en"
    desks = body["data"]
    assert len(desks) >= 5
    slugs = {desk["slug"] for desk in desks}
    assert "legal" in slugs

    desk = next(item for item in desks if item["slug"] == "legal")
    assert set(desk) == {
        "slug",
        "name",
        "tagline",
        "locales",
        "accent",
        "layout",
        "offers",
        "fetch_interval_minutes",
        "latest_published_at",
    }
    assert desk["accent"].startswith("#")
    assert desk["layout"] in {"editorial", "professional", "academic"}
    assert set(desk["offers"]) == {"brief", "asset", "question", "consultation"}
    assert all(isinstance(value, bool) for value in desk["offers"].values())
    assert isinstance(desk["fetch_interval_minutes"], int | None)
    latest = desk["latest_published_at"]
    assert latest is None or latest.endswith("Z")


@pytest.mark.asyncio
async def test_desks_localizes_the_tagline_only(client) -> None:
    """The board lists a desk once, in the requested locale, with stable fields."""
    english = (await client.get("/v1/desks?locale=en")).json()["data"]
    spanish = (await client.get("/v1/desks?locale=es")).json()["data"]
    assert [desk["slug"] for desk in english] == [desk["slug"] for desk in spanish]
    by_slug = {desk["slug"]: desk for desk in spanish}
    legal = by_slug["legal"]
    assert legal["tagline"]
    assert legal["layout"] == next(d["layout"] for d in english if d["slug"] == "legal")


@pytest.mark.asyncio
async def test_desks_rejects_unknown_query(client) -> None:
    response = await client.get("/v1/desks?limit=5")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_a_disabled_channel_leaves_the_lobby(admin_client, client) -> None:
    """Disabling a desk must remove it from the apex, not just from its own host.

    The lobby is generated from `/v1/desks`, so this also covers the board, the
    footer and the sitemap, which all read the same list.
    """
    before = {desk["slug"] for desk in (await client.get("/v1/desks")).json()["data"]}
    assert "legal" in before

    disabled = await admin_client.patch("/v1/admin/industries/legal", json={"enabled": False})
    assert disabled.status_code == 200, disabled.text

    after = {desk["slug"] for desk in (await client.get("/v1/desks")).json()["data"]}
    assert "legal" not in after
    assert after == before - {"legal"}
    assert (await client.get("/v1/industries/legal")).status_code == 404

    restored = await admin_client.patch("/v1/admin/industries/legal", json={"enabled": True})
    assert restored.status_code == 200
    assert "legal" in {desk["slug"] for desk in (await client.get("/v1/desks")).json()["data"]}
