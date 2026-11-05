from news_api.channels.domain.theme import DEFAULT_THEMES, contrast_ratio, validate_theme


def test_seed_themes_pass_contrast_checks() -> None:
    for variant, theme in DEFAULT_THEMES.items():
        problems = validate_theme(theme)
        assert problems == [], f"{variant}: {problems}"


def test_contrast_ratio_is_symmetric() -> None:
    assert contrast_ratio("#000000", "#ffffff") == contrast_ratio("#ffffff", "#000000")


def test_invalid_theme_reports_missing_tokens() -> None:
    problems = validate_theme({"primary": "#000000"})
    assert problems


def test_low_contrast_is_rejected() -> None:
    theme = dict(DEFAULT_THEMES["editorial"])
    theme["text"] = "#f5f5f5"
    problems = validate_theme(theme)
    assert any("text on background" in problem for problem in problems)
