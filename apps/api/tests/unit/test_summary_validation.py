from news_api.articles.infrastructure.ai_client import (
    AIError,
    normalize_brief,
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


def test_normalize_brief_turns_a_paragraph_into_lines() -> None:
    paragraph = (
        "OpenSSH released a patch for a critical flaw. Attackers can bypass password "
        "checks on musl-based systems. Administrators should upgrade immediately. "
        "Exploitation has not been observed yet."
    )
    brief = normalize_brief(paragraph)
    assert len(brief.splitlines()) == 4
    ok, reason = validate_brief(brief)
    assert ok, reason


def test_normalize_brief_keeps_existing_lines() -> None:
    brief = normalize_brief("Line one.\nLine two.\nLine three.")
    assert brief.splitlines() == ["Line one.", "Line two.", "Line three."]


# --- improvement plan Track D (D1-D5, D7) -----------------------------------

BASE = (
    "Regulators published new compliance guidance for banks this week. "
    "The rule cuts reporting deadlines to five days and requires updated documentation."
)


def test_valid_summary_still_passes_the_tighter_shape() -> None:
    ok, reason = validate_summary(BASE, "Banks face new compliance guidance")
    assert ok, reason


def test_summary_is_capped_at_three_sentences() -> None:
    text = BASE + " Banks must apply the rule by Monday. Enforcement starts in March."
    ok, reason = validate_summary(text, "Banks face new compliance guidance")
    assert not ok
    assert reason == "sentences"


def test_summary_is_capped_at_520_characters() -> None:
    text = (
        "Regulators published new compliance guidance for banks this week and the rule "
        "cuts reporting deadlines to five days while requiring updated documentation "
        "for every regulated bank in the region, which means compliance teams now have "
        "to rewrite their reporting calendar before the end of the quarter, confirm "
        "each change with their supervisor in writing, retrain every analyst who "
        "touches the report, and reconcile the new fields with the systems they "
        "already file through today without dropping a single historic entry or "
        "asking any bank to resend what it already sent."
    )
    assert len(text) > 520
    ok, reason = validate_summary(text, "Banks face new compliance guidance")
    assert not ok
    assert reason == "length"


def test_article_opener_is_rejected_and_proper_noun_opener_is_not() -> None:
    buried = (
        "The change shortens reporting deadlines for every regulated bank in the region "
        "and requires updated documentation before the end of the quarter. Banks must "
        "apply it by Monday."
    )
    ok, reason = validate_summary(buried, "Banks face new compliance guidance")
    assert not ok
    assert reason == "opener"

    actor_first = (
        "The European Commission published new compliance guidance for banks this week. "
        "The rule cuts reporting deadlines to five days and requires updated documents."
    )
    ok, reason = validate_summary(actor_first, "Banks face new compliance guidance")
    assert ok, reason


def test_first_sentence_may_not_exceed_25_words() -> None:
    long_open = (
        "Regulators published a set of new compliance guidance documents for banks "
        "operating across the whole region this week after a consultation that ran "
        "for eleven months with the industry. The rule cuts reporting deadlines."
    )
    assert len(long_open.split(".")[0].split()) > 25
    ok, reason = validate_summary(long_open, "Guidance for banks")
    assert not ok
    assert reason == "opener-length"


def test_stock_phrases_are_rejected_in_both_languages() -> None:
    english = (
        "Regulators published new compliance guidance for banks this week. "
        "For professional readers, the takeaway is that reporting gets shorter."
    )
    ok, reason = validate_summary(english, "Banks face new compliance guidance")
    assert not ok
    assert reason.startswith("banned-phrase:")

    spanish = (
        "Los reguladores publicaron nuevas normas para los bancos esta semana. "
        "El movimiento resulta relevante para los profesionales del sector financiero."
    )
    ok, reason = validate_summary(spanish, "Nuevas normas para bancos")
    assert not ok
    assert reason.startswith("banned-phrase:")


def test_vague_meaning_verbs_are_rejected() -> None:
    text = (
        "Regulators published new compliance guidance for banks this week. "
        "The move highlights a shift toward shorter reporting deadlines for lenders."
    )
    ok, reason = validate_summary(text, "Banks face new compliance guidance")
    assert not ok
    assert reason == "banned-verb"


def test_pointer_to_a_link_the_reader_cannot_follow_is_rejected() -> None:
    text = (
        "Regulators published new compliance guidance for banks this week. "
        "The full list of changes is in the notes; see URL in Notes for details."
    )
    ok, reason = validate_summary(text, "Banks face new compliance guidance")
    assert not ok
    assert reason == "reference"


def test_summary_keeps_the_number_when_the_source_has_one() -> None:
    title = "Freight rates fall 9.6% in October"
    without = (
        "Carriers cut spot rates again this month after demand weakened across the "
        "major trade lanes, and brokers expect the decline to continue into winter. "
        "Shippers are renegotiating contracts."
    )
    ok, reason = validate_summary(without, title, excerpt="Tonnage fell on the Asia-Europe lane.")
    assert not ok
    assert reason == "missing-number"
    with_digit = (
        "Carriers cut spot rates 9.6% this month after demand weakened across the "
        "major trade lanes, and brokers expect the decline to continue into winter. "
        "Shippers are renegotiating contracts."
    )
    ok, reason = validate_summary(
        with_digit, title, excerpt="Tonnage fell on the Asia-Europe lane."
    )
    assert ok, reason


def test_summary_without_source_digits_needs_none() -> None:
    ok, reason = validate_summary(BASE, "Banks face new compliance guidance", excerpt="Guidance.")
    assert ok, reason
