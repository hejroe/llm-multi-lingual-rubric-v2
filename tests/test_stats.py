import math

import pytest

from analysis.stats import (
    clopper_pearson_interval,
    cochrans_q,
    holm_bonferroni,
    mcnemar_exact,
)


def test_mcnemar_no_discordant_pairs_is_not_significant():
    result = mcnemar_exact(0, 0)
    assert result.p_value == 1.0


def test_mcnemar_symmetric_discordance_is_not_significant():
    # b == c is the case of maximum support for the null (p=0.5); the exact
    # two-sided binomial test must return p=1.0 exactly.
    result = mcnemar_exact(5, 5)
    assert result.p_value == 1.0


def test_mcnemar_one_sided_discordance_is_significant():
    # All discordant pairs favour one direction — a textbook clear-cut case.
    result = mcnemar_exact(0, 12)
    assert result.p_value < 0.001


def test_mcnemar_textbook_example():
    # A commonly-cited worked example (b=10, c=3): exact two-sided p ~ 0.09
    result = mcnemar_exact(10, 3)
    assert result.n_discordant == 13
    assert result.p_value == pytest.approx(0.0923, abs=0.001)


def test_clopper_pearson_known_reference_interval():
    # n=10, successes=5: a standard textbook reference interval ~ (0.187, 0.812)
    interval = clopper_pearson_interval(successes=5, n=10, alpha=0.05)
    assert interval.point_estimate == 0.5
    assert interval.lower == pytest.approx(0.1871, abs=0.001)
    assert interval.upper == pytest.approx(0.8129, abs=0.001)


def test_clopper_pearson_edge_cases():
    zero = clopper_pearson_interval(successes=0, n=10)
    assert zero.lower == 0.0
    assert zero.upper < 1.0

    full = clopper_pearson_interval(successes=10, n=10)
    assert full.upper == 1.0
    assert full.lower > 0.0


def test_cochrans_q_hand_verified_small_case():
    # Hand-computed: column totals [2,2,3], row totals [2,2,2,1], grand=7,
    # k=3 -> numerator=2*(3*17-49)=4, denominator=3*7-13=8 -> Q=0.5, df=2.
    # For df=2, the chi-square survival function has the closed form
    # exp(-x/2) exactly -- independently checkable without trusting scipy
    # circularly.
    matrix = [[1, 0, 1], [0, 1, 1], [1, 1, 0], [0, 0, 1]]
    result = cochrans_q(matrix)
    assert result.statistic == pytest.approx(0.5)
    assert result.df == 2
    assert result.p_value == pytest.approx(math.exp(-0.25), abs=1e-9)


def test_cochrans_q_perfect_agreement_has_no_variation_to_test():
    matrix = [[1, 1, 1], [0, 0, 0], [1, 1, 1]]
    result = cochrans_q(matrix)
    assert result.p_value == 1.0


def test_cochrans_q_accepts_a_single_row_with_at_least_two_conditions():
    # One item is a degenerate but legitimate input; only the condition
    # count and row-length consistency are actually required.
    result = cochrans_q([[1, 0]])
    assert result.df == 1


def test_cochrans_q_rejects_ragged_or_too_few_conditions():
    with pytest.raises(ValueError):
        cochrans_q([[1]])  # only 1 condition
    with pytest.raises(ValueError):
        cochrans_q([[1, 0, 1], [1, 0]])  # ragged


def test_holm_bonferroni_step_down_property():
    # A classic worked case: three p-values, alpha=0.05.
    # sorted: 0.01 (thresh .05/3=.0167, reject), 0.03 (thresh .05/2=.025, NOT rejected -> stop)
    p_values = [0.03, 0.01, 0.20]
    reject = holm_bonferroni(p_values, alpha=0.05)
    assert reject == [False, True, False]


def test_holm_bonferroni_all_rejected():
    p_values = [0.0001, 0.0002, 0.0003]
    reject = holm_bonferroni(p_values, alpha=0.05)
    assert reject == [True, True, True]
