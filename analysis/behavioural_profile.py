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
