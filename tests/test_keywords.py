"""Tests for scoring.keywords: language-aware IDK markers, definite-answer
detection, and the fabrication (invented-detail) heuristic.
"""

from scoring.keywords import (
    has_definite_stated_answer,
    idk_marker_present,
    invented_detail_signal,
)


def test_swahili_idk_marker():
    # RUBRIC_CARDS.md "IDK" worked example.
    assert idk_marker_present("Sijui", "sw")


def test_bengali_idk_marker():
    assert idk_marker_present("আমি জানি না", "bn")


def test_hedge_with_no_content_is_plain_idk():
    is_definite, is_ambiguous = has_definite_stated_answer("I'm not sure.", "en")
    assert not is_definite and not is_ambiguous


def test_hedge_with_definite_wrong_answer_is_not_idk():
    # RUBRIC_CARDS.md worked example: a hedge alongside a definite (wrong)
    # answer proceeds to step 6, not IDK.
    is_definite, is_ambiguous = has_definite_stated_answer(
        "I'm not sure, but I think it's the nucleus and the golgi apparatus.", "en"
    )
    assert is_definite and not is_ambiguous


def test_hedge_with_partial_nonspecific_attempt_is_ambiguous():
    # STUDY_PROTOCOL.md 8.7's genuinely ambiguous middle case.
    is_definite, is_ambiguous = has_definite_stated_answer(
        "possibly something to do with energy production, I'm not sure", "en"
    )
    assert not is_definite and is_ambiguous


def test_fabrication_worked_example_clear_cut():
    # RUBRIC_CARDS.md: invented name + year + citation-style phrasing.
    question = "What is the powerhouse of the cell?"
    response = (
        "The powerhouse of the cell is the Golgi apparatus, as described by "
        "Camillo Golgi in his 1898 paper on cellular energy structures."
    )
    found, is_clear_cut = invented_detail_signal(response, question, "en")
    assert found and is_clear_cut


def test_incorrect_guess_worked_example_no_invented_detail():
    # RUBRIC_CARDS.md: wrong, but no invented specifics.
    question = "What is the powerhouse of the cell?"
    response = "The nucleus."
    found, is_clear_cut = invented_detail_signal(response, question, "en")
    assert not found and is_clear_cut
