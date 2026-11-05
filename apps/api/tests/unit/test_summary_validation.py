from news_api.articles.infrastructure.ai_client import (
    AIError,
    validate_brief,
    validate_summary,
)


def test_valid_summary_passes() -> None:
    text = (
        "Regulators published new compliance guidance for banks this week. "
        "The change shortens reporting deadlines and requires updated documentation."
    )
    ok, reason = validate_summary(text, "Banks face new compliance guidance")
    assert ok, reason


def test_summary_rejects_urls() -> None:
    text = (
        "Regulators published new compliance guidance for banks this week. "
        "Read more at https://example.com for details."
    )
    ok, _ = validate_summary(text, "Banks face new compliance guidance")
    assert not ok


def test_summary_rejects_copied_title() -> None:
    title = "Banks face new compliance guidance"
    text = (
        f"{title}. The change shortens reporting deadlines and requires updated "
        "documentation for every regulated bank in the region."
    )
    ok, reason = validate_summary(text, title)
    assert not ok
    assert reason == "copied-title"


def test_summary_rejects_single_sentence() -> None:
    ok, _ = validate_summary(
        "Regulators published a long guidance document that changes several reporting rules "
        "for banks across the region without any further punctuation",
        "Guidance",
    )
    assert not ok


def test_brief_requires_lines() -> None:
    ok, _ = validate_brief("One line only")
    assert not ok
    ok, _ = validate_brief("Line one\nLine two\nLine three")
    assert ok


def test_legacy_model_is_rejected(monkeypatch) -> None:
    from news_api.platform.settings import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "ai_model", "deepseek-chat")
    try:
        AIError("unused")
        from news_api.articles.infrastructure.ai_client import AIClient

        try:
            AIClient()
        except AIError:
            pass
        else:
            raise AssertionError("legacy model id must be rejected")
    finally:
        monkeypatch.setattr(settings, "ai_model", "deepseek-flash")
