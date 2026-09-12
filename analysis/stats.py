"""The exact/non-parametric statistical primitives STUDY_PROTOCOL.md Section
10 fixes in advance (10.3, 10.5): McNemar's exact test, Clopper-Pearson
exact intervals, Cochran's Q, and Holm-Bonferroni correction. These are the
one place in this project that pulls in `scipy` — reimplementing exact
distributional math (the incomplete beta/gamma functions Clopper-Pearson
and Cochran's Q ultimately need) from scratch would risk exactly the kind
of subtle numerical bug 10.5 exists to avoid; scipy's implementations are
the standard, independently-tested choice instead.
"""

from __future__ import annotations

from dataclasses import dataclass

from scipy import stats as scipy_stats


@dataclass
class McNemarResult:
    statistic: int  # the smaller discordant-pair count, per the exact/sign-test formulation
    n_discordant: int
    p_value: float


def mcnemar_exact(b: int, c: int) -> McNemarResult:
    """McNemar's exact test (10.3) on a paired binary comparison's two
    discordant-pair counts: `b` = condition-1-yes/condition-2-no, `c` =
    the reverse. Equivalent to an exact two-sided binomial sign test on the
    discordant pairs against p=0.5 (ADR 0002) — the standard exact
    formulation, preferred over the chi-square approximation at the small
    sample sizes this pilot uses (10.5).
    """
    n = b + c
    if n == 0:
        return McNemarResult(statistic=0, n_discordant=0, p_value=1.0)
    result = scipy_stats.binomtest(min(b, c), n=n, p=0.5, alternative="two-sided")
    return McNemarResult(statistic=min(b, c), n_discordant=n, p_value=result.pvalue)


@dataclass
class ClopperPearsonInterval:
    point_estimate: float
    lower: float
    upper: float


def clopper_pearson_interval(successes: int, n: int, alpha: float = 0.05) -> ClopperPearsonInterval:
    """The exact binomial confidence interval STUDY_PROTOCOL.md 10.3
    specifies for RQ3's descriptive proportions (Current-and-Correct /
    Stale-Asserted-as-Current / Flagged-Uncertain-Appropriately rates),
    since a formal hypothesis test may be underpowered at pilot sample
    sizes (10.5) — reported descriptively with an exact interval instead.
    """
    if n == 0:
        return ClopperPearsonInterval(point_estimate=0.0, lower=0.0, upper=1.0)
    point_estimate = successes / n
    lower = 0.0 if successes == 0 else scipy_stats.beta.ppf(alpha / 2, successes, n - successes + 1)
    upper = 1.0 if successes == n else scipy_stats.beta.ppf(1 - alpha / 2, successes + 1, n - successes)
    return ClopperPearsonInterval(point_estimate=point_estimate, lower=lower, upper=upper)


@dataclass
class CochranQResult:
    statistic: float
    df: int
    p_value: float


def cochrans_q(binary_matrix: list[list[int]]) -> CochranQResult:
    """Cochran's Q test (10.3, RQ7's US/UK/AU three-way paired comparison):
    `binary_matrix[i]` is one item's [condition_1, condition_2, ...
    condition_k] outcomes (1/0), the same item scored under every
    condition. Raises ValueError if any row isn't the same length, or if
    there are fewer than 2 conditions.
    """
    n_items = len(binary_matrix)
    if n_items == 0:
        raise ValueError("cochrans_q requires at least one item")
    k = len(binary_matrix[0])
    if k < 2:
        raise ValueError("cochrans_q requires at least 2 conditions")
    if any(len(row) != k for row in binary_matrix):
        raise ValueError("every row must have the same number of conditions")

    column_totals = [sum(row[j] for row in binary_matrix) for j in range(k)]
    row_totals = [sum(row) for row in binary_matrix]
    grand_total = sum(row_totals)

    numerator = (k - 1) * (k * sum(t * t for t in column_totals) - grand_total * grand_total)
    denominator = k * grand_total - sum(t * t for t in row_totals)

    if denominator == 0:
        # Every item agrees across every condition (all-0 or all-1 rows) —
        # no variation to test; not a computable statistic, not a p=1 claim.
        return CochranQResult(statistic=0.0, df=k - 1, p_value=1.0)

    q_statistic = numerator / denominator
    df = k - 1
    p_value = scipy_stats.chi2.sf(q_statistic, df)
    return CochranQResult(statistic=q_statistic, df=df, p_value=p_value)


def holm_bonferroni(p_values: list[float], alpha: float = 0.05) -> list[bool]:
    """Holm-Bonferroni step-down correction (10.5) over the primary
    comparison set (one test per RQ, selected before any result is seen).
    Returns, for each input p-value (same order as given), whether it's
    rejected (significant) under the correction.
    """
    n = len(p_values)
    order = sorted(range(n), key=lambda i: p_values[i])
    reject = [False] * n
    for rank, i in enumerate(order):
        threshold = alpha / (n - rank)
        if p_values[i] <= threshold:
            reject[i] = True
        else:
            # Once one step fails, every remaining (larger) p-value is
            # also not rejected — the defining step-down property.
            break
    return reject
