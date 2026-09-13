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


def test_shows_arithmetic_working_detects_shown_steps():
    assert shows_arithmetic_working("3 x 8 = 25, 25 - 5 = 20")
    assert not shows_arithmetic_working("The answer is 20.")
