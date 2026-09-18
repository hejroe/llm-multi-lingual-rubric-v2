"""Tests for scoring.matching: think-block stripping/extraction (Section
11's reasoning-trace audit trail), variety-aware gold-answer matching, and
arithmetic-working detection.
"""

from scoring.matching import (
    extract_think_blocks,
    matches_gold_answer,
    shows_arithmetic_working,
    strip_think_blocks,
)


def test_strip_think_blocks_removes_reasoning_before_matching():
    # 8.5: prevents the original repo's chain-of-thought-leakage bug.
    response = "<think>The answer is definitely the nucleus.</think>The mitochondria."
    assert "nucleus" not in strip_think_blocks(response)
    assert matches_gold_answer(strip_think_blocks(response), "mitochondria")


def test_extract_think_blocks_preserves_what_strip_think_blocks_discards():
    # Added 2026-09-12 (ADR 0010) — the reasoning trace is kept for audit
    # (Section 11), not just thrown away once used for matching.
    response = "<think>The answer is definitely the nucleus.</think>The mitochondria."
    stripped, reasoning = extract_think_blocks(response)
    assert stripped == strip_think_blocks(response)
    assert reasoning == "<think>The answer is definitely the nucleus.</think>"


def test_extract_think_blocks_none_when_nothing_to_strip():
    stripped, reasoning = extract_think_blocks("The mitochondria.")
    assert stripped == "The mitochondria."
    assert reasoning is None


def test_correct_german_trailing_article_and_punctuation_not_a_barrier():
    # RUBRIC_CARDS.md "Correct" worked example.
    assert matches_gold_answer("Die Mitochondrien.", "Mitochondrien")


def test_set_f_variety_spelling_is_not_automatically_wrong():
    # RUBRIC_CARDS.md "Correct" common confusion: a UK/AU item answered with
    # the "wrong" (US) spelling is not on that basis alone incorrect.
    assert matches_gold_answer("The flag is coloured blue, white, and red.", "colour")
    assert matches_gold_answer("It is colored blue, white, and red.", "colour")


def test_no_gold_answer_never_matches():
    # Set B's unspecified-jurisdiction variant carries no gold_answer (5.6).
    assert not matches_gold_answer("Eighteen.", "")


def test_numeric_gold_answer_does_not_match_embedded_in_a_larger_number():
    # Regression (2026-09-13): a plain substring test made "18" match
    # inside "1800s" or "218 dollars" -- exactly the shape Sets B (ages)
    # and C (rates) use throughout, so this was a live false-positive
    # risk, not a hypothetical one.
    assert not matches_gold_answer("The law dates back to the 1800s.", "18")
    assert not matches_gold_answer("It costs 218 dollars.", "18")
    assert matches_gold_answer("You must be 18 to buy this.", "18")


def test_numeric_gold_answer_with_trailing_symbol_still_matches():
    # Regression (2026-09-13): a naive \b-based boundary check fails when
    # the gold answer itself ends in a non-word character (e.g. "%"),
    # since \b requires a word/non-word transition and neither side of
    # "...25%" + end-of-string is a word character.
    assert matches_gold_answer("25%", "25%")
    assert matches_gold_answer("The rate is 25% this year.", "25%")


def test_shows_arithmetic_working_detects_shown_steps():
    assert shows_arithmetic_working("3 x 8 = 25, 25 - 5 = 20")
    assert not shows_arithmetic_working("The answer is 20.")


def test_bengali_digit_numeral_matches_latin_gold_answer():
    # Regression (2026-09-16): Bengali digit glyphs (০-৯, U+09E6-U+09EF)
    # have no NFKD decomposition to Latin digits, so a Bengali-scripted
    # numeric answer never matched a gold_answer stored in Latin digits --
    # every gold_answer in this corpus is, whether from the vendored
    # MGSM-Rev2 TSVs or hand-authored Set B/C content. This understated
    # Bengali Correct-rate for any model answering with Bengali numerals.
    assert matches_gold_answer("উত্তর হল ৭০০০০ ডলার।", "70000")
    assert matches_gold_answer("আপনার বয়স ১৮ হতে হবে।", "18")


def test_bengali_digit_numeral_still_respects_word_boundary():
    # The Bengali-digit translation must not defeat the existing embedded-
    # number protection (2026-09-13 regression, above): "১৮০০" translates
    # to "1800", which must not register as containing gold "18".
    assert not matches_gold_answer("মূল্য ১৮০০ টাকা।", "18")
