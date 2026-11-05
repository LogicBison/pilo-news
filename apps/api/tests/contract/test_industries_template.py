from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_operator_can_create_a_new_industry(admin_client, client) -> None:
    payload = {
        "slug": "e2e-vertical",
        "code": "E2E_VERTICAL",
        "name": "E2E Vertical",
        "theme": {"layout": "academic", "primary": "#1d4ed8", "accent": "#b45309"},
        "locales": {
            "en": {"name": "E2E Vertical", "tagline": "A template channel."},
            "es": {"name": "Vertical E2E", "tagline": "Un canal de plantilla."},
        },
        "disclaimers": {
            "en": "News, not professional advice.",
            "es": "Noticias, no asesoría profesional.",
        },
        "cta": {
            "kind": "consultation",
            "headline": {"en": "Talk to a partner", "es": "Hable con un socio"},
            "body": {"en": "Tell us what you need.", "es": "Cuéntenos qué necesita."},
            "label": {"en": "Request a consultation", "es": "Solicitar una consulta"},
        },
        "topics": [
            {
                "slug": "standards",
                "label": {"en": "Standards", "es": "Normas"},
                "weight": 1.2,
                "keywords": {"en": ["standard"], "es": ["norma"]},
            }
        ],
    }
    created = await admin_client.post("/v1/admin/industries", json=payload)
    assert created.status_code == 201, created.text
    data = created.json()["data"]
    assert data["slug"] == "e2e-vertical"
    assert data["enabled"] is True
    assert data["theme"]["layout"] == "academic"

    listed = await client.get("/v1/industries")
    assert "e2e-vertical" in {item["slug"] for item in listed.json()["data"]}
    detail = await client.get("/v1/industries/e2e-vertical?locale=es")
    assert detail.status_code == 200
    assert detail.json()["data"]["name"] == "Vertical E2E"
    topics = await admin_client.get("/v1/admin/topics?industry=e2e-vertical")
    assert topics.status_code == 200
    assert topics.json()["data"][0]["slug"] == "standards"


@pytest.mark.asyncio
async def test_industry_creation_validates_theme_and_slug(admin_client) -> None:
    low_contrast = {
        "slug": "e2e-bad",
        "code": "E2E_BAD",
        "name": "E2E Bad",
        "theme": {"layout": "editorial", "text": "#ffffff", "bg": "#ffffff"},
    }
    response = await admin_client.post("/v1/admin/industries", json=low_contrast)
    assert response.status_code == 422

    reserved = {
        "slug": "admin",
        "code": "RESERVED",
        "name": "Reserved",
    }
    response = await admin_client.post("/v1/admin/industries", json=reserved)
    assert response.status_code == 422
