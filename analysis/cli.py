"""Run the Section 10 per-RQ analyses over one or more scored JSONL files
(scoring.cli's output).

Usage:
    python -m analysis.cli --scored results/scored/*.jsonl

Best-effort: an RQ whose required paired data isn't present in the given
files (e.g. RQ1 needs both a baseline language and at least one comparison
language actually scored) is reported as skipped, not silently omitted or
crashed on — this pilot's data grows incrementally, and which RQs are
answerable depends on which tasks have actually been run and scored so far.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from analysis.behavioural_profile import behavioural_profile
from analysis.reliability import compute_reliability
from analysis.rq_analysis import (
    correct_primary_confirmatory_set,
    rq1_language_gap,
    rq2_jurisdiction_default,
    rq3_currency_descriptive,
    rq6_contamination_check,
    rq7_variety_triplet,
)

PRIMARY_LANGUAGE = (
    "de"  # STUDY_PROTOCOL.md 10.5, confirmed by the study owner 2026-09-08
)


def _load_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def _by(rows: list[dict], **filters) -> list[dict]:
    return [r for r in rows if all(r.get(k) == v for k, v in filters.items())]


def _primary_domain(rows: list[dict], family: str) -> str | None:
    """10.5: "the primary domain is whichever domain has the largest item
    count once the corpus is built" — an objective, outcome-independent
    rule fixed in advance, not a domain name chosen before the corpus
    exists. Ties break alphabetically, for a deterministic result."""
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        if r.get("family") == family and r.get("domain"):
            counts[r["domain"]] += 1
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scored",
        required=True,
        nargs="+",
        type=Path,
        help="one or more scored JSONL files",
    )
    args = parser.parse_args(argv)

    rows = _load_rows(args.scored)
    print(f"loaded {len(rows)} scored rows from {len(args.scored)} file(s)\n")

    # Primary-confirmatory-set p-values (10.5), assembled as each RQ below
    # actually produces one, then Holm-Bonferroni-corrected together at the
    # end — only RQs whose primary comparison is actually available given
    # the corpus scored so far are included, consistent with this module's
    # existing "skip, don't fabricate" policy.
    primary_p_values: dict[str, float] = {}

    print("=== Behavioural Response Profile (10.2), by language ===")
    profile_items = behavioural_profile(rows, group_by=("language",)).items()
    for key, counter in sorted(
        profile_items, key=lambda kv: tuple(str(x) for x in kv[0])
    ):
        print(f"  {key}: {dict(counter)}")

    print("\n=== Reliability (10.4), by model ===")
    reliability = compute_reliability(rows, group_by=("model_name",))
    if reliability:
        for key, result in reliability.items():
            print(
                f"  {key}: {result.n_fully_agreeing}/{result.n_items} items fully "
                f"agree ({result.agreement_rate:.1%})"
            )
    else:
        print("  skipped: no rows to group")

    print("\n=== RQ1: Correct-rate, per language pair, per domain (10.3) ===")
    other_languages = sorted(
        {r["language"] for r in rows if r.get("family") == "A"} - {"en"}
    )
    domains = sorted(
        {r["domain"] for r in rows if r.get("family") == "A" and r.get("domain")}
    )
    primary_domain = _primary_domain(rows, family="A")
    if not other_languages or not domains:
        print("  skipped: needs Set A rows in English plus at least one other language")
    else:
        for domain in domains:
            for lang in other_languages:
                en_rows = _by(rows, family="A", language="en", domain=domain)
                other_rows = _by(rows, family="A", language=lang, domain=domain)
                result = rq1_language_gap(en_rows, other_rows)
                is_primary = lang == PRIMARY_LANGUAGE and domain == primary_domain
                tag = " [PRIMARY]" if is_primary else ""
                if result.n_pairs == 0:
                    print(
                        f"  en vs {lang} ({domain}){tag}: "
                        "skipped (no paired items found)"
                    )
                    continue
                print(
                    f"  en vs {lang} ({domain}){tag}: n={result.n_pairs}, "
                    f"en={result.condition_a_rate:.1%}, "
                    f"{lang}={result.condition_b_rate:.1%}, "
                    f"McNemar p={result.mcnemar.p_value:.4f}"
                )
                if is_primary:
                    primary_p_values["RQ1"] = result.mcnemar.p_value

    print("\n=== RQ2: Jurisdiction-Adaptation, unspecified vs specified (10.3) ===")
    b_languages = sorted({r["language"] for r in rows if r.get("family") == "B"})
    if not b_languages:
        print("  skipped: no Set B rows")
    else:
        for lang in b_languages:
            unspecified_rows = [
                r
                for r in rows
                if r.get("family") == "B"
                and r.get("language") == lang
                and not r.get("jurisdiction")
            ]
            specified_rows = [
                r
                for r in rows
                if r.get("family") == "B"
                and r.get("language") == lang
                and r.get("jurisdiction")
            ]
            is_primary = lang == PRIMARY_LANGUAGE
            tag = " [PRIMARY]" if is_primary else ""
            if not unspecified_rows or not specified_rows:
                print(
                    f"  {lang}{tag}: skipped (needs both unspecified and "
                    "jurisdiction-specified Set B rows)"
                )
                continue
            result = rq2_jurisdiction_default(unspecified_rows, specified_rows)
            if result.n_pairs == 0:
                print(f"  {lang}{tag}: skipped (no paired items found)")
                continue
            unspecified_rate = result.unspecified_wrong_default_rate
            specified_rate = result.specified_wrong_default_rate
            print(
                f"  {lang}{tag}: n={result.n_pairs}, "
                f"unspecified wrong-default rate={unspecified_rate:.1%}, "
                f"specified wrong-default rate={specified_rate:.1%}, "
                f"McNemar p={result.mcnemar.p_value:.4f}"
            )
            if is_primary:
                primary_p_values["RQ2"] = result.mcnemar.p_value

    print("\n=== RQ3: Currency-Awareness, descriptive (10.3) ===")
    set_c_rows = [r for r in rows if r.get("family") == "C"]
    if not set_c_rows:
        print("  skipped: no Set C rows")
    else:
        result = rq3_currency_descriptive(set_c_rows)
        for label, interval in [
            ("Current-and-Correct", result.current_and_correct),
            ("Stale-Asserted-as-Current", result.stale_asserted_as_current),
            ("Flagged-Uncertain-Appropriately", result.flagged_uncertain_appropriately),
        ]:
            print(
                f"  {label}: {interval.point_estimate:.1%} "
                f"(95% CI {interval.lower:.1%}-{interval.upper:.1%})"
            )

    print("\n=== RQ6: Contamination check, Set A vs Set E (10.3) ===")
    e_languages = sorted({r["language"] for r in rows if r.get("family") == "E"})
    if not e_languages:
        print("  skipped: no Set E rows")
    else:
        for lang in e_languages:
            set_a_rows = _by(rows, family="A", language=lang)
            set_e_rows = _by(rows, family="E", language=lang)
            is_primary = lang == PRIMARY_LANGUAGE
            tag = " [PRIMARY]" if is_primary else ""
            if not set_a_rows or not set_e_rows:
                print(
                    f"  {lang}{tag}: skipped (needs Set A and Set E rows "
                    "in this language)"
                )
                continue
            result = rq6_contamination_check(set_a_rows, set_e_rows)
            if result.n_pairs == 0:
                print(f"  {lang}{tag}: skipped (no paired items found)")
                continue
            flag = (
                "CONTAMINATION-INDICATIVE"
                if result.contamination_indicative
                else "not indicative"
            )
            print(
                f"  {lang}{tag}: n={result.n_pairs}, "
                f"original={result.original_correct_rate:.1%}, "
                f"perturbed={result.perturbed_correct_rate:.1%}, "
                f"drop={result.percentage_point_drop:.1f}pp ({flag}), "
                f"McNemar p={result.mcnemar.p_value:.4f}"
            )
            if is_primary:
                primary_p_values["RQ6"] = result.mcnemar.p_value
        if PRIMARY_LANGUAGE not in e_languages:
            print(
                f"  note: no Set E rows in the primary language ({PRIMARY_LANGUAGE}) "
                "yet — RQ6 has no primary-set entry for this run"
            )

    print("\n=== RQ7: US/UK/AU variety triplet (10.3) ===")
    us_rows = _by(rows, family="A", language="en", domain="knowledge")
    uk_rows = _by(rows, family="F", variety="UK")
    au_rows = _by(rows, family="F", variety="AU")
    if not us_rows or not uk_rows or not au_rows:
        print("  skipped: needs Set A (en, knowledge) and Set F (UK, AU) rows")
    else:
        result = rq7_variety_triplet(us_rows, uk_rows, au_rows)
        if result.n_items == 0:
            print("  skipped: no paired items found")
        else:
            print(f"  n={result.n_items}, rates={result.correct_rates}")
            print(
                f"  Cochran's Q={result.cochrans_q.statistic:.3f}, "
                f"df={result.cochrans_q.df}, p={result.cochrans_q.p_value:.4f}"
            )
            primary_p_values["RQ7"] = result.cochrans_q.p_value
            if result.pairwise_mcnemar:
                for pair, mcnemar_result in result.pairwise_mcnemar.items():
                    sig = (
                        "significant"
                        if result.pairwise_significant[pair]
                        else "not significant"
                    )
                    print(
                        f"    {pair}: p={mcnemar_result.p_value:.4f} "
                        f"({sig}, Holm-Bonferroni-corrected)"
                    )
            else:
                print("  (Q not significant — pairwise comparisons not run, per 10.3)")

    print(
        "\n=== Primary confirmatory set (10.5): "
        "Holm-Bonferroni-corrected across RQs ==="
    )
    if not primary_p_values:
        print("  skipped: no RQ's primary comparison is available yet")
    else:
        correction = correct_primary_confirmatory_set(primary_p_values)
        for label, raw_p, sig in zip(
            correction.labels,
            correction.raw_p_values,
            correction.corrected_significant,
            strict=True,
        ):
            verdict = "significant" if sig else "not significant"
            print(f"  {label}: raw p={raw_p:.4f} -> {verdict} (corrected, alpha=0.05)")
        missing = {"RQ1", "RQ2", "RQ6", "RQ7"} - set(primary_p_values)
        if missing:
            print(
                f"  note: {', '.join(sorted(missing))} not yet part of this "
                "correction — primary comparison unavailable given the "
                "corpus scored so far"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
