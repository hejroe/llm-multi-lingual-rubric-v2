"""Tests for analysis.rq_analysis: the Section 10.3 RQ1-RQ7 statistical
tests (McNemar pairs, Cochran's Q with Holm-Bonferroni-corrected
pairwise follow-ups, Clopper-Pearson intervals).
"""

import pytest

from analysis.rq_analysis import (
    correct_primary_confirmatory_set,
    rq1_language_gap,
    rq2_jurisdiction_default,
    rq3_currency_descriptive,
    rq6_contamination_check,
    rq7_variety_triplet,
)


def _row(question_id, category, **extra):
    row = {"question_id": question_id, "category": category}
    row.update(extra)
    return row


# --- RQ1 ---------------------------------------------------------------


def test_rq1_language_gap_hand_computed():
    en_rows = [
        _row("A-1-en", "Correct"),
        _row("A-2-en", "Correct"),
        _row("A-3-en", "Incorrect-Guess"),
    ]
    de_rows = [
        _row(
            "A-1-de", "Incorrect-Guess", language_variant_of="A-1-en"
        ),  # discordant: en correct, de wrong
        _row("A-2-de", "Correct", language_variant_of="A-2-en"),  # concordant
        _row(
            "A-3-de", "Correct", language_variant_of="A-3-en"
        ),  # discordant: en wrong, de correct
    ]
    result = rq1_language_gap(en_rows, de_rows)
    assert result.n_pairs == 3
    assert result.condition_a_rate == pytest.approx(2 / 3)
    assert result.condition_b_rate == pytest.approx(2 / 3)
    # b=1, c=1 -> symmetric discordance -> p=1.0 exactly
    assert result.mcnemar.p_value == 1.0


def test_rq1_ignores_unpaired_rows():
    en_rows = [_row("A-1-en", "Correct")]
    de_rows = [
        _row("A-9-de", "Correct", language_variant_of="A-9-en")
    ]  # no matching baseline
    result = rq1_language_gap(en_rows, de_rows)
    assert result.n_pairs == 0


def test_rq1_collapses_replicates_via_majority_vote_not_last_write_wins():
    # Regression (2026-09-13): 3 replicates per item (9.3) on each side must
    # collapse to ONE pair per item, not one pair per replicate (which would
    # inflate n_pairs and break McNemar's independence assumption), and the
    # collapsed outcome must not simply be whichever replicate loaded last.
    en_rows = [
        _row("A-1-en", "Correct"),
        _row("A-1-en", "Correct"),
        _row("A-1-en", "Incorrect-Guess"),  # 2/3 Correct -> majority Correct
    ]
    de_rows = [
        _row("A-1-de", "Incorrect-Guess", language_variant_of="A-1-en"),
        _row("A-1-de", "Incorrect-Guess", language_variant_of="A-1-en"),
        _row(
            "A-1-de", "Correct", language_variant_of="A-1-en"
        ),  # 1/3 Correct -> majority Incorrect
    ]
    result = rq1_language_gap(en_rows, de_rows)
    assert result.n_pairs == 1  # one item, not 3 (or 9)
    assert result.condition_a_rate == 1.0  # en majority: Correct
    assert result.condition_b_rate == 0.0  # de majority: Incorrect-Guess


def test_rq1_majority_vote_tie_resolves_to_not_correct():
    en_rows = [
        _row("A-1-en", "Correct"),
        _row("A-1-en", "Incorrect-Guess"),
    ]  # 1/2 -> tie -> not Correct
    de_rows = [_row("A-1-de", "Correct", language_variant_of="A-1-en")]
    result = rq1_language_gap(en_rows, de_rows)
    assert result.condition_a_rate == 0.0


# --- RQ6 ---------------------------------------------------------------


def test_rq6_contamination_check_above_threshold():
    original_rows = [
        _row("A-1-en", "Correct"),
        _row("A-2-en", "Correct"),
        _row("A-3-en", "Correct"),
        _row("A-4-en", "Correct"),
    ]
    perturbed_rows = [
        _row("E-1", "Correct", language_variant_of="A-1-en"),
        _row("E-2", "Correct", language_variant_of="A-2-en"),
        _row("E-3", "Correct", language_variant_of="A-3-en"),
        _row("E-4", "Incorrect-Guess", language_variant_of="A-4-en"),
    ]
    result = rq6_contamination_check(original_rows, perturbed_rows)
    assert result.n_pairs == 4
    assert result.original_correct_rate == 1.0
    assert result.perturbed_correct_rate == 0.75
    assert result.percentage_point_drop == pytest.approx(25.0)
    assert result.contamination_indicative is True


def test_rq6_contamination_check_below_threshold():
    original_rows = [_row(f"A-{i}-en", "Correct") for i in range(1, 21)]
    perturbed_rows = [
        _row(f"E-{i}", "Correct", language_variant_of=f"A-{i}-en") for i in range(1, 20)
    ]
    perturbed_rows.append(
        _row("E-20", "Incorrect-Guess", language_variant_of="A-20-en")
    )  # 1/20 = 5pp exactly at boundary -> not below
    result = rq6_contamination_check(
        original_rows, perturbed_rows, threshold_points=10.0
    )
    assert result.percentage_point_drop == pytest.approx(5.0)
    assert result.contamination_indicative is False  # 5 < 10


# --- RQ7 ---------------------------------------------------------------


def test_rq7_variety_triplet_significant_q_triggers_pairwise():
    us_rows, uk_rows, au_rows = [], [], []
    for i in range(10):
        qid = f"A-{i}-en"
        us_rows.append(_row(qid, "Correct"))
        uk_rows.append(_row(f"F-{i}-UK", "Correct", language_variant_of=qid))
        au_rows.append(_row(f"F-{i}-AU", "Incorrect-Guess", language_variant_of=qid))

    result = rq7_variety_triplet(us_rows, uk_rows, au_rows)
    assert result.n_items == 10
    assert result.correct_rates == {"us": 1.0, "uk": 1.0, "au": 0.0}
    assert result.cochrans_q.statistic == pytest.approx(20.0)
    assert result.cochrans_q.p_value < 0.001

    assert result.pairwise_mcnemar is not None
    assert result.pairwise_mcnemar["us_vs_uk"].p_value == 1.0  # fully concordant
    assert result.pairwise_significant["us_vs_uk"] is False
    assert result.pairwise_significant["us_vs_au"] is True
    assert result.pairwise_significant["uk_vs_au"] is True


def test_rq7_variety_triplet_no_variation_is_not_significant():
    us_rows, uk_rows, au_rows = [], [], []
    for i in range(6):
        qid = f"A-{i}-en"
        us_rows.append(_row(qid, "Correct"))
        uk_rows.append(_row(f"F-{i}-UK", "Correct", language_variant_of=qid))
        au_rows.append(_row(f"F-{i}-AU", "Correct", language_variant_of=qid))

    result = rq7_variety_triplet(us_rows, uk_rows, au_rows)
    assert result.cochrans_q.p_value == 1.0
    assert result.pairwise_mcnemar is None
    assert result.pairwise_significant is None


def test_rq7_collapses_replicates_via_majority_vote():
    # Regression (2026-09-13): same independence-assumption fix as RQ1.
    us_rows = [_row("A-1-en", "Correct"), _row("A-1-en", "Correct")]
    uk_rows = [
        _row("F-1-UK", "Correct", language_variant_of="A-1-en"),
        _row("F-1-UK", "Incorrect-Guess", language_variant_of="A-1-en"),
        _row("F-1-UK", "Incorrect-Guess", language_variant_of="A-1-en"),
    ]  # majority: Incorrect-Guess
    au_rows = [_row("F-1-AU", "Correct", language_variant_of="A-1-en")]

    result = rq7_variety_triplet(us_rows, uk_rows, au_rows)
    assert result.n_items == 1  # one item, not one pair per replicate
    assert result.correct_rates == {"us": 1.0, "uk": 0.0, "au": 1.0}


# --- RQ3 -----------------------------------------------------------------


def test_rq3_currency_descriptive():
    rows = [
        _row("C-1-v1-en", "Correct", currency_awareness="Stale-Asserted-as-Current"),
        _row(
            "C-1-v2-en", "Fabrication", currency_awareness="Stale-Asserted-as-Current"
        ),
        _row("C-2-v1-en", "IDK", currency_awareness="Flagged-Uncertain-Appropriately"),
        _row("C-2-v2-en", "Correct", currency_awareness="Current-and-Correct"),
    ]
    result = rq3_currency_descriptive(rows)
    assert result.n_items == 4
    assert result.stale_asserted_as_current.point_estimate == 0.5
    assert result.flagged_uncertain_appropriately.point_estimate == 0.25
    assert result.current_and_correct.point_estimate == 0.25


# --- RQ2 -----------------------------------------------------------------


def test_rq2_jurisdiction_default_hand_computed():
    unspecified_rows = [
        _row(
            "B-ALC-01-unspecified-en",
            "Fabrication",
            jurisdiction_adaptation="Wrong-Jurisdiction-Default",
        ),
        _row(
            "B-CRIM-01-unspecified-en",
            "Correct",
            jurisdiction_adaptation="Jurisdiction-Ignored",
        ),
    ]
    specified_rows = [
        _row(
            "B-ALC-01-UK-en",
            "Correct",
            jurisdiction_adaptation="Correct-for-Jurisdiction",
        ),
        _row(
            "B-CRIM-01-UK-en",
            "Correct",
            jurisdiction_adaptation="Wrong-Jurisdiction-Default",
        ),
    ]
    result = rq2_jurisdiction_default(unspecified_rows, specified_rows)
    assert result.n_pairs == 2
    assert result.unspecified_wrong_default_rate == 0.5
    assert result.specified_wrong_default_rate == 0.5
    # b=1 (ALC: unspecified wrong, specified not), c=1 (CRIM: specified wrong, unspecified not) -> symmetric
    assert result.mcnemar.p_value == 1.0


def test_rq2_handles_multiple_jurisdiction_specified_variants_per_base_fact():
    # Regression (2026-09-13): a base fact with N specified variants (5.5's
    # own worked example, B-ALC-01, has UK and US) must produce N separate
    # pairs against the shared unspecified outcome, not silently keep only
    # whichever variant loaded last.
    unspecified_rows = [
        _row(
            "B-ALC-01-unspecified-en",
            "Fabrication",
            jurisdiction_adaptation="Wrong-Jurisdiction-Default",
        )
    ]
    specified_rows = [
        _row(
            "B-ALC-01-UK-en",
            "Correct",
            jurisdiction_adaptation="Correct-for-Jurisdiction",
        ),
        _row(
            "B-ALC-01-US-en",
            "Correct",
            jurisdiction_adaptation="Correct-for-Jurisdiction",
        ),
    ]
    result = rq2_jurisdiction_default(unspecified_rows, specified_rows)
    assert result.n_pairs == 2  # both UK and US variants counted, not 1
    assert result.unspecified_wrong_default_rate == 1.0
    assert result.specified_wrong_default_rate == 0.0


def test_rq2_collapses_replicates_of_the_same_variant_via_majority_vote():
    unspecified_rows = [
        _row(
            "B-ALC-01-unspecified-en",
            "Fabrication",
            jurisdiction_adaptation="Wrong-Jurisdiction-Default",
        ),
        _row(
            "B-ALC-01-unspecified-en",
            "Correct",
            jurisdiction_adaptation="Correct-for-Jurisdiction",
        ),
        _row(
            "B-ALC-01-unspecified-en",
            "Fabrication",
            jurisdiction_adaptation="Wrong-Jurisdiction-Default",
        ),  # 2/3 replicates wrong -> majority wrong
    ]
    specified_rows = [
        _row(
            "B-ALC-01-UK-en",
            "Correct",
            jurisdiction_adaptation="Correct-for-Jurisdiction",
        )
    ]
    result = rq2_jurisdiction_default(unspecified_rows, specified_rows)
    assert result.n_pairs == 1
    assert result.unspecified_wrong_default_rate == 1.0


# --- Primary confirmatory set correction (10.5) ---------------------------


def test_correct_primary_confirmatory_set_applies_holm_bonferroni():
    result = correct_primary_confirmatory_set(
        {"RQ1": 0.01, "RQ2": 0.04, "RQ6": 0.20, "RQ7": 0.03}
    )
    assert result.labels == ["RQ1", "RQ2", "RQ6", "RQ7"]
    assert result.raw_p_values == [0.01, 0.04, 0.20, 0.03]
    # Holm-Bonferroni, alpha=0.05, 4 tests, sorted p-values [0.01,0.03,0.04,0.20]
    # vs thresholds [0.0125,0.0167,0.025,0.05]: 0.01 rejects (<=0.0125), 0.03
    # fails (>0.0167) and stops the step-down -> only RQ1 significant.
    assert result.corrected_significant == [True, False, False, False]


def test_correct_primary_confirmatory_set_empty_when_no_rq_available():
    result = correct_primary_confirmatory_set({})
    assert result.labels == []
    assert result.corrected_significant == []
