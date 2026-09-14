"""The Behavioural Response Profile (STUDY_PROTOCOL.md 10.2) — the one
shared summary shape every RQ-specific analysis draws from: a category
distribution per condition, rather than each RQ inventing its own.
"""

from __future__ import annotations

from collections import Counter, defaultdict


def behavioural_profile(
    scored_rows: list[dict], group_by: tuple[str, ...]
) -> dict[tuple, Counter]:
    """Distribution across the 8.2 primary categories, grouped by whichever
    condition fields are named in `group_by` (e.g. `("language",)`,
    `("family", "language")`, `("model_name", "language")` — any field
    present in a scored row, including the provenance fields `scoring.io`
    stamps onto it).
    """
    profiles: dict[tuple, Counter] = defaultdict(Counter)
    for row in scored_rows:
        key = tuple(row.get(field) for field in group_by)
        profiles[key][row["category"]] += 1
    return dict(profiles)


def infrastructure_failure_rate(
    scored_rows: list[dict], group_by: tuple[str, ...]
) -> dict[tuple, float]:
    """10.7: Infrastructure-Failure rate, reported as its own statistic
    per model and per backend (or any other grouping, e.g. language) —
    separate from, never folded into, the capability metrics in 10.3.
    Added 2026-09-14: this was a Protocol-stated reporting requirement
    with no corresponding function anywhere in `analysis/` — the rate was
    only visible by manually reading raw counts out of
    `behavioural_profile`'s output. Motivated by a real finding in the
    first full pilot run: `smollm2:1.7b` (documented "primarily English"
    in the Model Register) returned a genuinely empty completion for
    64% of its Bengali items — a real, substantial, model-specific
    robustness gap easy to miss without this being a first-class,
    per-model, per-language statistic.
    """
    counts: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])  # [failures, total]
    for row in scored_rows:
        key = tuple(row.get(field) for field in group_by)
        counts[key][1] += 1
        if row["category"] == "Infrastructure-Failure":
            counts[key][0] += 1
    return {
        key: (failures / total if total else 0.0)
        for key, (failures, total) in counts.items()
    }


def overlay_profile(
    scored_rows: list[dict], overlay_field: str, group_by: tuple[str, ...]
) -> dict[tuple, Counter]:
    """Same as `behavioural_profile`, but over one of the 8.3 overlay
    fields (`jurisdiction_adaptation`, `currency_awareness`,
    `tool_invocation`) instead of the primary category — rows where that
    overlay wasn't applicable (value is `None`) are excluded, not counted
    as a category of their own.
    """
    profiles: dict[tuple, Counter] = defaultdict(Counter)
    for row in scored_rows:
        value = row.get(overlay_field)
        if value is None:
            continue
        key = tuple(row.get(field) for field in group_by)
        profiles[key][value] += 1
    return dict(profiles)
