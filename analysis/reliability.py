"""The reliability/consistency metric (STUDY_PROTOCOL.md 10.4): using the
9.3 replication (each item queried 3 times per model per condition), the
proportion of items where every replicate receives the same primary
category — reported per model, per condition, rather than silently
averaging repeated runs together.

This operates on however many replicate rows are actually present per
`question_id` within `scored_rows` (grouped by `group_by`, typically at
least `model_name`) — it does not hardcode "3", since no run at the full
9.3 replication count has happened yet; pass in scored rows from N
concatenated runs of the same task/model to get N-way agreement.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ReliabilityResult:
    n_items: int
    n_fully_agreeing: int
    agreement_rate: float


def compute_reliability(
    scored_rows: list[dict], group_by: tuple[str, ...] = ("model_name",)
) -> dict[tuple, ReliabilityResult]:
    by_item: dict[tuple, list[str]] = defaultdict(list)
    for row in scored_rows:
        key = tuple(row.get(field) for field in group_by) + (row["question_id"],)
        by_item[key].append(row["category"])

    totals: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])  # [n_items, n_fully_agreeing]
    for key, categories in by_item.items():
        condition_key = key[:-1]
        totals[condition_key][0] += 1
        if len(set(categories)) == 1:
            totals[condition_key][1] += 1

    return {
        condition_key: ReliabilityResult(
            n_items=n_items,
            n_fully_agreeing=n_agreeing,
            agreement_rate=(n_agreeing / n_items) if n_items else 0.0,
        )
        for condition_key, (n_items, n_agreeing) in totals.items()
    }
