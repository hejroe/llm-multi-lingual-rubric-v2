"""Per-RQ analysis methods (STUDY_PROTOCOL.md 10.3), operating on the flat
scored rows `scoring.io.write_scored_jsonl` produces (each carrying
`question_id`, `category`, the 8.3 overlay fields, and item-context fields
including `language_variant_of` — the join key every pairing below uses).

RQ4 (tool-calling calibration) is not implemented here: it needs Set D
responses with an actual tool-call signal, which the harness setup this
project currently uses cannot capture (see scoring/io.py's module
docstring) and which is blocked on GPU passthrough for the llamacpp
backend in any case. RQ5 is a downstream interpretive judgement (10.6),
not a statistical test of its own — no function here computes it.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from analysis.stats import (
    ClopperPearsonInterval,
    CochranQResult,
    McNemarResult,
    clopper_pearson_interval,
    cochrans_q,
    holm_bonferroni,
    mcnemar_exact,
)

_CORRECT_CATEGORIES = {"Correct", "Correct-Process"}


def _index_by_question_id(rows: list[dict]) -> dict[str, dict]:
    return {row["question_id"]: row for row in rows}


def _is_correct(row: dict) -> bool:
    return row["category"] in _CORRECT_CATEGORIES


@dataclass
class PairedPointResult:
    n_pairs: int
    condition_a_rate: float
    condition_b_rate: float
    mcnemar: McNemarResult


def rq1_language_gap(scored_rows: list[dict], other_language_rows: list[dict]) -> PairedPointResult:
    """RQ1 (10.3): Correct-category rate, same items across a language
    pair. `scored_rows` is the primary-language (baseline) condition;
    `other_language_rows` is the comparison language, paired via
    `language_variant_of` pointing back to `scored_rows`' question_ids.
    """
    baseline_by_id = _index_by_question_id(scored_rows)
    b = c = 0  # discordant pairs: b = baseline-correct/other-wrong, c = the reverse
    n_pairs = 0
    baseline_correct_count = other_correct_count = 0

    for other_row in other_language_rows:
        variant_of = other_row.get("language_variant_of")
        if variant_of not in baseline_by_id:
            continue
        baseline_row = baseline_by_id[variant_of]
        n_pairs += 1
        baseline_ok = _is_correct(baseline_row)
        other_ok = _is_correct(other_row)
        baseline_correct_count += baseline_ok
        other_correct_count += other_ok
        if baseline_ok and not other_ok:
            b += 1
        elif other_ok and not baseline_ok:
            c += 1

    return PairedPointResult(
        n_pairs=n_pairs,
        condition_a_rate=baseline_correct_count / n_pairs if n_pairs else 0.0,
        condition_b_rate=other_correct_count / n_pairs if n_pairs else 0.0,
        mcnemar=mcnemar_exact(b, c),
    )


@dataclass
class ContaminationCheckResult:
    n_pairs: int
    original_correct_rate: float
    perturbed_correct_rate: float
    percentage_point_drop: float
    contamination_indicative: bool  # 10.3's 5-point threshold
    mcnemar: McNemarResult


def rq6_contamination_check(
    original_rows: list[dict], perturbed_rows: list[dict], threshold_points: float = 5.0
) -> ContaminationCheckResult:
    """RQ6 (10.3): Correct-rate, Set A original vs its Set E perturbed
    twin, per model — paired via `language_variant_of` on the Set E rows.
    A drop of >= `threshold_points` percentage points is treated as
    contamination-indicative (10.3), independent of whether the paired
    McNemar test is itself significant at this pilot's small sample sizes.
    """
    paired = rq1_language_gap(original_rows, perturbed_rows)
    drop = (paired.condition_a_rate - paired.condition_b_rate) * 100
    return ContaminationCheckResult(
        n_pairs=paired.n_pairs,
        original_correct_rate=paired.condition_a_rate,
        perturbed_correct_rate=paired.condition_b_rate,
        percentage_point_drop=drop,
        contamination_indicative=drop >= threshold_points,
        mcnemar=paired.mcnemar,
    )


@dataclass
class VarietyTripletResult:
    n_items: int
    correct_rates: dict[str, float]  # "us" | "uk" | "au" -> rate
    cochrans_q: CochranQResult
    pairwise_mcnemar: dict[str, McNemarResult] | None  # only computed if Q is significant
    pairwise_significant: dict[str, bool] | None  # Holm-Bonferroni-corrected


def rq7_variety_triplet(
    us_rows: list[dict], uk_rows: list[dict], au_rows: list[dict], alpha: float = 0.05
) -> VarietyTripletResult:
    """RQ7 (10.3): Correct-rate across the US/UK/AU triplet — Cochran's Q
    first; pairwise McNemar with Holm-Bonferroni correction only if Q is
    significant, per 10.3's stated procedure. UK/AU rows are paired back to
    their US originals via `language_variant_of`.
    """
    us_by_id = _index_by_question_id(us_rows)
    uk_by_variant = {r["language_variant_of"]: r for r in uk_rows}
    au_by_variant = {r["language_variant_of"]: r for r in au_rows}

    matrix = []
    common_ids = [qid for qid in us_by_id if qid in uk_by_variant and qid in au_by_variant]
    for qid in common_ids:
        matrix.append([
            int(_is_correct(us_by_id[qid])),
            int(_is_correct(uk_by_variant[qid])),
            int(_is_correct(au_by_variant[qid])),
        ])

    n_items = len(matrix)
    correct_rates = {
        variety: (sum(row[i] for row in matrix) / n_items if n_items else 0.0)
        for i, variety in enumerate(["us", "uk", "au"])
    }

    if n_items == 0:
        q_result = CochranQResult(statistic=0.0, df=2, p_value=1.0)
    else:
        q_result = cochrans_q(matrix)

    pairwise_mcnemar = pairwise_significant = None
    if q_result.p_value < alpha:
        pair_names = ["us_vs_uk", "us_vs_au", "uk_vs_au"]
        pair_indices = [(0, 1), (0, 2), (1, 2)]
        pairwise_mcnemar = {}
        for name, (i, j) in zip(pair_names, pair_indices):
            b = sum(1 for row in matrix if row[i] == 1 and row[j] == 0)
            c = sum(1 for row in matrix if row[j] == 1 and row[i] == 0)
            pairwise_mcnemar[name] = mcnemar_exact(b, c)
        p_values = [pairwise_mcnemar[name].p_value for name in pair_names]
        rejections = holm_bonferroni(p_values, alpha=alpha)
        pairwise_significant = dict(zip(pair_names, rejections))

    return VarietyTripletResult(
        n_items=n_items,
        correct_rates=correct_rates,
        cochrans_q=q_result,
        pairwise_mcnemar=pairwise_mcnemar,
        pairwise_significant=pairwise_significant,
    )


@dataclass
class CurrencyDescriptiveResult:
    n_items: int
    stale_asserted_as_current: ClopperPearsonInterval
    flagged_uncertain_appropriately: ClopperPearsonInterval
    current_and_correct: ClopperPearsonInterval


def rq3_currency_descriptive(set_c_rows: list[dict], alpha: float = 0.05) -> CurrencyDescriptiveResult:
    """RQ3 (10.3): descriptive proportions with exact (Clopper-Pearson)
    intervals over Set C's Currency-Awareness overlay — reported
    descriptively rather than as a formal test, since this pilot's Set C
    sample size may be underpowered for one (10.5)."""
    n = len(set_c_rows)
    counts = defaultdict(int)
    for row in set_c_rows:
        if row.get("currency_awareness"):
            counts[row["currency_awareness"]] += 1

    def interval(label: str) -> ClopperPearsonInterval:
        return clopper_pearson_interval(counts.get(label, 0), n, alpha=alpha)

    return CurrencyDescriptiveResult(
        n_items=n,
        stale_asserted_as_current=interval("Stale-Asserted-as-Current"),
        flagged_uncertain_appropriately=interval("Flagged-Uncertain-Appropriately"),
        current_and_correct=interval("Current-and-Correct"),
    )


@dataclass
class JurisdictionDefaultResult:
    n_pairs: int
    unspecified_wrong_default_rate: float
    specified_wrong_default_rate: float
    mcnemar: McNemarResult


def rq2_jurisdiction_default(
    unspecified_rows: list[dict], specified_rows: list[dict]
) -> JurisdictionDefaultResult:
    """RQ2 (10.3): Jurisdiction-Adaptation overlay, unspecified vs
    jurisdiction-specified variant. Interpretive choice, stated plainly
    since 10.3 names the comparison but not its exact binary outcome: the
    paired outcome here is "did this response default to the wrong
    jurisdiction" (`Wrong-Jurisdiction-Default`, 8.3) for the unspecified
    variant, compared against the same indicator for its jurisdiction-
    specified sibling (paired via the shared base-fact id derived the same
    way `scoring.io._base_fact_id` does, since both variants share it).
    """
    from scoring.io import _base_fact_id  # local import: analysis depends on scoring, not vice versa

    specified_by_base = {}
    for row in specified_rows:
        base = _base_fact_id(row["question_id"])
        if base:
            specified_by_base[base] = row

    b = c = 0
    n_pairs = 0
    unspecified_wrong = specified_wrong = 0

    for row in unspecified_rows:
        base = _base_fact_id(row["question_id"])
        if base not in specified_by_base:
            continue
        specified_row = specified_by_base[base]
        n_pairs += 1
        unspecified_is_wrong = row.get("jurisdiction_adaptation") == "Wrong-Jurisdiction-Default"
        specified_is_wrong = specified_row.get("jurisdiction_adaptation") == "Wrong-Jurisdiction-Default"
        unspecified_wrong += unspecified_is_wrong
        specified_wrong += specified_is_wrong
        if unspecified_is_wrong and not specified_is_wrong:
            b += 1
        elif specified_is_wrong and not unspecified_is_wrong:
            c += 1

    return JurisdictionDefaultResult(
        n_pairs=n_pairs,
        unspecified_wrong_default_rate=unspecified_wrong / n_pairs if n_pairs else 0.0,
        specified_wrong_default_rate=specified_wrong / n_pairs if n_pairs else 0.0,
        mcnemar=mcnemar_exact(b, c),
    )
