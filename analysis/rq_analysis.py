"""Per-RQ analysis methods (STUDY_PROTOCOL.md 10.3), operating on the flat
scored rows `scoring.io.write_scored_jsonl` produces (each carrying
`question_id`, `category`, the 8.3 overlay fields, and item-context fields
including `language_variant_of` — the join key every pairing below uses).

Every pairing function below collapses replicate rows (9.3's 3x
replication; possibly more, ADR 0003) to one outcome per item *before*
forming a pair, via `_aggregate_by_key`'s majority vote — found necessary
2026-09-13 after review: with replicated data, keying a plain dict by
`question_id` silently keeps only the last-loaded replicate for one side
of a pair while the other side's loop still iterated every replicate row
as its own pair, inflating `n_pairs` and violating the independence
McNemar's exact test assumes. Reliability *across* those replicates is a
separate, deliberately distinct metric (10.4, `analysis/reliability.py`)
— this collapsing answers "was this item correct" for the RQ-level test,
it does not also try to measure agreement, which is what 10.4 is for.

RQ4 (tool-calling calibration) is not implemented here: it needs Set D
responses with an actual tool-call signal, which the harness setup this
project currently uses cannot capture (see scoring/io.py's module
docstring) and which is blocked on GPU passthrough for the llamacpp
backend in any case. RQ5 is a downstream interpretive judgement (10.6),
not a statistical test of its own — no function here computes it.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
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


def _is_correct(row: dict) -> bool:
    return row["category"] in _CORRECT_CATEGORIES


def _majority_vote(values: list[bool]) -> bool:
    """Strict majority; an even split (a tie) resolves to False — a hung
    jury across replicates is not evidence of a definite positive outcome
    either way, and this keeps the rule from depending on replicate order."""
    return sum(values) * 2 > len(values)


def _aggregate_by_key(
    rows: list[dict],
    key_fn: Callable[[dict], str | None],
    predicate: Callable[[dict], bool],
) -> dict[str, bool]:
    """Collapse every row sharing the same `key_fn(row)` (typically several
    replicates of the same item/condition, 9.3) to one boolean via majority
    vote of `predicate(row)`. Rows whose key is `None` are dropped, not
    counted."""
    groups: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        key = key_fn(row)
        if key is not None:
            groups[key].append(predicate(row))
    return {key: _majority_vote(values) for key, values in groups.items()}


@dataclass
class PairedPointResult:
    n_pairs: int
    condition_a_rate: float
    condition_b_rate: float
    mcnemar: McNemarResult


def rq1_language_gap(
    scored_rows: list[dict], other_language_rows: list[dict]
) -> PairedPointResult:
    """RQ1 (10.3): Correct-category rate, same items across a language
    pair. `scored_rows` is the primary-language (baseline) condition;
    `other_language_rows` is the comparison language, paired via
    `language_variant_of` pointing back to `scored_rows`' question_ids.
    """
    baseline_correct = _aggregate_by_key(
        scored_rows, lambda r: r["question_id"], _is_correct
    )
    other_correct = _aggregate_by_key(
        other_language_rows, lambda r: r.get("language_variant_of"), _is_correct
    )

    common_ids = sorted(set(baseline_correct) & set(other_correct))
    n_pairs = len(common_ids)
    b = c = 0
    baseline_correct_count = other_correct_count = 0

    for qid in common_ids:
        baseline_ok = baseline_correct[qid]
        other_ok = other_correct[qid]
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


def rq8_backend_divergence(
    backend_a_rows: list[dict], backend_b_rows: list[dict]
) -> PairedPointResult:
    """RQ8 (10.3, added 2026-09-19): Correct-category rate, same items,
    same model, same parameters, across a backend pair (e.g. Ollama vs
    llama.cpp) -- paired directly by `question_id` on *both* sides, unlike
    RQ1's language pairing, since backend choice doesn't change which item
    this is (no `language_variant_of` indirection needed). Callers must
    pre-filter both row lists to one model (and, for Qwen3, be aware the
    Ollama side runs without reasoning-mode control -- 10.3's RQ8 method
    notes)."""
    a_correct = _aggregate_by_key(
        backend_a_rows, lambda r: r["question_id"], _is_correct
    )
    b_correct = _aggregate_by_key(
        backend_b_rows, lambda r: r["question_id"], _is_correct
    )

    common_ids = sorted(set(a_correct) & set(b_correct))
    n_pairs = len(common_ids)
    b = c = 0
    a_correct_count = b_correct_count = 0

    for qid in common_ids:
        a_ok = a_correct[qid]
        b_ok = b_correct[qid]
        a_correct_count += a_ok
        b_correct_count += b_ok
        if a_ok and not b_ok:
            b += 1
        elif b_ok and not a_ok:
            c += 1

    return PairedPointResult(
        n_pairs=n_pairs,
        condition_a_rate=a_correct_count / n_pairs if n_pairs else 0.0,
        condition_b_rate=b_correct_count / n_pairs if n_pairs else 0.0,
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
    pairwise_mcnemar: (
        dict[str, McNemarResult] | None
    )  # only computed if Q is significant
    pairwise_significant: dict[str, bool] | None  # Holm-Bonferroni-corrected


def rq7_variety_triplet(
    us_rows: list[dict], uk_rows: list[dict], au_rows: list[dict], alpha: float = 0.05
) -> VarietyTripletResult:
    """RQ7 (10.3): Correct-rate across the US/UK/AU triplet — Cochran's Q
    first; pairwise McNemar with Holm-Bonferroni correction only if Q is
    significant, per 10.3's stated procedure. UK/AU rows are paired back to
    their US originals via `language_variant_of`.
    """
    us_correct = _aggregate_by_key(us_rows, lambda r: r["question_id"], _is_correct)
    uk_correct = _aggregate_by_key(
        uk_rows, lambda r: r.get("language_variant_of"), _is_correct
    )
    au_correct = _aggregate_by_key(
        au_rows, lambda r: r.get("language_variant_of"), _is_correct
    )

    common_ids = sorted(set(us_correct) & set(uk_correct) & set(au_correct))
    matrix = [
        [int(us_correct[qid]), int(uk_correct[qid]), int(au_correct[qid])]
        for qid in common_ids
    ]

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
        for name, (i, j) in zip(pair_names, pair_indices, strict=True):
            b = sum(1 for row in matrix if row[i] == 1 and row[j] == 0)
            c = sum(1 for row in matrix if row[j] == 1 and row[i] == 0)
            pairwise_mcnemar[name] = mcnemar_exact(b, c)
        p_values = [pairwise_mcnemar[name].p_value for name in pair_names]
        rejections = holm_bonferroni(p_values, alpha=alpha)
        pairwise_significant = dict(zip(pair_names, rejections, strict=True))

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


def rq3_currency_descriptive(
    set_c_rows: list[dict], alpha: float = 0.05
) -> CurrencyDescriptiveResult:
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
    specified sibling(s), paired via the shared base-fact id (the same
    derivation `scoring.io._base_fact_id` uses).

    A base fact can have *N* jurisdiction-specified siblings (5.5's
    worked example, `B-ALC-01`, has two: UK and US) — each is its own
    pairing against the shared unspecified outcome for that base fact,
    not collapsed into a single "specified" summary per base fact. Found
    2026-09-13: a plain `{base: row}` dict silently kept only the
    last-loaded sibling, dropping the other from this confirmatory test
    non-reproducibly (dependent on row order). Replicates of the *same*
    variant (same question_id) are still collapsed via majority vote
    first, same as every other RQ here.
    """
    from scoring.io import (
        _base_fact_id,
    )  # local import: analysis depends on scoring, not vice versa

    def is_wrong_default(row: dict) -> bool:
        return row.get("jurisdiction_adaptation") == "Wrong-Jurisdiction-Default"

    unspecified_wrong_by_base = _aggregate_by_key(
        unspecified_rows,
        lambda r: _base_fact_id(r["question_id"]),
        is_wrong_default,
    )
    # Collapse replicates of each *specific* jurisdiction variant first
    # (same question_id => same variant), keeping distinct variants (e.g.
    # -UK- vs -US-) as distinct entries.
    specified_wrong_by_variant = _aggregate_by_key(
        specified_rows, lambda r: r["question_id"], is_wrong_default
    )
    variant_base = {
        row["question_id"]: _base_fact_id(row["question_id"]) for row in specified_rows
    }

    b = c = 0
    n_pairs = 0
    unspecified_wrong_sum = specified_wrong_sum = 0

    for variant_qid, specified_is_wrong in specified_wrong_by_variant.items():
        base = variant_base[variant_qid]
        if base not in unspecified_wrong_by_base:
            continue
        unspecified_is_wrong = unspecified_wrong_by_base[base]
        n_pairs += 1
        unspecified_wrong_sum += unspecified_is_wrong
        specified_wrong_sum += specified_is_wrong
        if unspecified_is_wrong and not specified_is_wrong:
            b += 1
        elif specified_is_wrong and not unspecified_is_wrong:
            c += 1

    return JurisdictionDefaultResult(
        n_pairs=n_pairs,
        unspecified_wrong_default_rate=unspecified_wrong_sum / n_pairs
        if n_pairs
        else 0.0,
        specified_wrong_default_rate=specified_wrong_sum / n_pairs if n_pairs else 0.0,
        mcnemar=mcnemar_exact(b, c),
    )


@dataclass
class PrimarySetCorrection:
    labels: list[str]
    raw_p_values: list[float]
    corrected_significant: list[bool]


def correct_primary_confirmatory_set(
    labeled_p_values: dict[str, float], alpha: float = 0.05
) -> PrimarySetCorrection:
    """10.5: the primary confirmatory set — one pre-selected test per RQ
    (RQ1's primary language+domain, RQ2's primary language, RQ6's primary
    language, RQ7's whole triplet, whichever of these are actually
    available given the corpus built so far) — is Holm-Bonferroni
    corrected together, family-wise. Found 2026-09-13: nothing previously
    assembled this set; each RQ's p-value was read at alpha on its own,
    which inflates the true family-wise error rate above 5% across the
    four confirmatory tests, contrary to what 10.5 specifies. `caller`
    decides which RQs are actually part of the set (per the corpus
    currently available — see analysis/cli.py) and passes only those.
    """
    labels = list(labeled_p_values.keys())
    p_values = [labeled_p_values[label] for label in labels]
    significant = holm_bonferroni(p_values, alpha=alpha) if p_values else []
    return PrimarySetCorrection(
        labels=labels, raw_p_values=p_values, corrected_significant=significant
    )
