from __future__ import annotations

from news_api.platform.utm import normalize_utm


def test_normalize_utm_keeps_only_known_keys_and_caps_length() -> None:
    value = normalize_utm(
        {
            "utm_source": "  newsletter ",
            "utm_campaign": "x" * 200,
            "utm_unknown": "drop",
            "not-a-string": 4,
        }
    )
    assert value["utm_source"] == "newsletter"
    assert len(value["utm_campaign"]) == 120
    assert "utm_unknown" not in value
    assert "not-a-string" not in value
    assert normalize_utm(None) == {}
    assert normalize_utm("nope") == {}
