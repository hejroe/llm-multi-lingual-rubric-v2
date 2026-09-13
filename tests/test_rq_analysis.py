import pytest

from analysis.rq_analysis import (
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
