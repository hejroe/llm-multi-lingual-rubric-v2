"""The scoring rubric decision logic (STUDY_PROTOCOL.md Section 8, rubric-v0.3).

`score_response` implements the 8.4 decision-logic steps in order. Each
step's rationale is the specific original-repo bug it prevents (8.5) — see
that section and RUBRIC_CARDS.md before changing the order.

This module assigns categories from a single response's text. The 8.3
overlay axes for Set B/C additionally need *sibling* rows (the same
underlying fact's other jurisdiction/version variants) to compare against —
callers building a scored dataset from a whole corpus (see `io.py`) pass
those in; this module does not load the corpus itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from scoring.categories import (
    ConfidenceTier,
    CurrencyAwareness,
    JurisdictionAdaptation,
    PrimaryCategory,
    ToolInvocationCalibration,
)
from scoring.keywords import (
    has_definite_stated_answer,
    idk_marker_present,
    invented_detail_signal,
)
from scoring.matching import extract_think_blocks, matches_gold_answer, shows_arithmetic_working


@dataclass
class ScoredResponse:
    question_id: str
    category: PrimaryCategory
    confidence_tier: ConfidenceTier | None = None
    jurisdiction_adaptation: JurisdictionAdaptation | None = None
    currency_awareness: CurrencyAwareness | None = None
    tool_invocation: ToolInvocationCalibration | None = None
    notes: list[str] = field(default_factory=list)
    # Preserved for audit (Section 11, added 2026-09-12/ADR 0010) rather
    # than discarded once used for matching — only recovers a trace
    # embedded in `content` behind <think> tags; see
    # scoring/matching.py's extract_think_blocks docstring for what this
    # does not capture.
    reasoning_trace: str | None = None


def _resolve_gold_text(item: dict) -> str:
    """Set A/F multiple-choice items carry an option letter as `gold_answer`
    (e.g. "E") plus `option_0`..`option_9` columns holding the actual answer
    text; every other family already carries the literal answer. Matching
    must be against the literal text either way.
    """
    gold = (item.get("gold_answer") or "").strip()
    if len(gold) == 1 and gold.isalpha():
        option_key = f"option_{ord(gold.upper()) - ord('A')}"
        option_text = item.get(option_key)
        if option_text:
            return option_text
    return gold


def is_infrastructure_failure(harness_error: str | None, response_text: str | None) -> bool:
    """8.4 step 1 / 8.2: an API error, timeout, or empty response — checked
    first, from the harness's own error/empty-body signal, never from text
    that merely talks about an error (RUBRIC_CARDS.md's Infrastructure-
    Failure card, common confusion)."""
    return bool(harness_error) or not (response_text and response_text.strip())


def score_response(
    *,
    question_id: str,
    item: dict,
    response_text: str | None,
    harness_error: str | None = None,
    sibling_jurisdiction_items: list[dict] | None = None,
    sibling_version_items: list[dict] | None = None,
    tool_call_invoked: bool | None = None,
) -> ScoredResponse:
    """Score one (item, response) pair per 8.4's decision logic.

    Args:
        item: a single corpus row (5.6 schema) as a dict, e.g. from
            `csv.DictReader`.
        response_text: the model's raw completion, before any processing.
        harness_error: the harness's own error/timeout signal for this
            request, if any (not text the model happened to generate).
        sibling_jurisdiction_items: for Set B, the other jurisdiction/
            unspecified variants of the same underlying fact (8.3).
        sibling_version_items: for Set C, the other effective-date versions
            of the same underlying fact (8.3).
        tool_call_invoked: for a `tool_required`-tagged item (Set D
            re-tagging, 5.5), whether the model actually invoked a tool —
            read from the harness's raw API response, not inferred from text.
    """
    language = item.get("language") or item.get("variety", "en")
    family = item.get("family")

    # Step 1: infrastructure failure, checked first, excludes every other axis.
    if is_infrastructure_failure(harness_error, response_text):
        return ScoredResponse(
            question_id=question_id,
            category=PrimaryCategory.INFRASTRUCTURE_FAILURE,
        )

    assert response_text is not None  # guaranteed non-empty by the check above

    # Step 2: strip reasoning/chain-of-thought before any text matching.
    # The extracted trace is preserved (not just discarded) for audit
    # (Section 11, ADR 0010) — see extract_think_blocks' own docstring for
    # what it does and doesn't capture.
    stripped_response, reasoning_trace = extract_think_blocks(response_text)

    # Step 3: language/variety-appropriate Correct match.
    gold_text = _resolve_gold_text(item)
    if matches_gold_answer(stripped_response, gold_text):
        result = ScoredResponse(
            question_id=question_id,
            category=PrimaryCategory.CORRECT,
            confidence_tier=ConfidenceTier.HIGH_CONFIDENCE,
        )
        _apply_overlays(
            result, item, stripped_response, sibling_jurisdiction_items,
            sibling_version_items, tool_call_invoked, language, reasoning_trace,
        )
        return result

    # Step 4: IDK, unless a definite stated alternative answer accompanies it.
    if idk_marker_present(stripped_response, language):
        is_definite, is_ambiguous = has_definite_stated_answer(stripped_response, language)
        if not is_definite and not is_ambiguous:
            result = ScoredResponse(
                question_id=question_id,
                category=PrimaryCategory.IDK,
                confidence_tier=ConfidenceTier.HIGH_CONFIDENCE,
            )
            _apply_overlays(
                result, item, stripped_response, sibling_jurisdiction_items,
                sibling_version_items, tool_call_invoked, language,
            )
            return result
        if is_ambiguous:
            # 8.7's genuinely ambiguous middle case: still commit to IDK,
            # but flag the call as a best-effort one.
            result = ScoredResponse(
                question_id=question_id,
                category=PrimaryCategory.IDK,
                confidence_tier=ConfidenceTier.HEURISTIC_GUIDANCE,
                notes=["idk-vs-wrong-answer: partial non-specific attempt alongside hedge"],
            )
            _apply_overlays(
                result, item, stripped_response, sibling_jurisdiction_items,
                sibling_version_items, tool_call_invoked, language,
            )
            return result
        # is_definite: a stated alternative answer is present — fall through
        # to step 6, not IDK, per 8.4 step 4 and RUBRIC_CARDS.md's worked
        # hedge example.

    # Step 5: procedural-reasoning items — Correct-Process.
    if family == "A" and item.get("domain") == "procedural" and shows_arithmetic_working(stripped_response):
        # The corpus does not (yet) carry a gold *method* annotation per
        # procedural item (only the final gold_answer, 5.6) — genuine
        # method-validity, as opposed to merely "some working shown", isn't
        # mechanically checkable from that alone. This is a best-effort
        # proxy (RUBRIC_CARDS.md: the qualifying signal is that a method was
        # shown at all, not that no method was correct), always tagged
        # Heuristic-Guidance and routed to the periodic manual/LLM-judge
        # audit (8.7) rather than asserted as a confident finding.
        result = ScoredResponse(
            question_id=question_id,
            category=PrimaryCategory.CORRECT_PROCESS,
            confidence_tier=ConfidenceTier.HEURISTIC_GUIDANCE,
            notes=["procedural item: shown working detected, method validity not independently verified"],
        )
        _apply_overlays(
            result, item, stripped_response, sibling_jurisdiction_items,
            sibling_version_items, tool_call_invoked, language, reasoning_trace,
        )
        return result

    # Step 6: Incorrect-Guess vs. Fabrication, by presence of invented detail.
    found_invented_detail, is_clear_cut = invented_detail_signal(
        stripped_response, item.get("question_text", ""), language
    )
    category = PrimaryCategory.FABRICATION if found_invented_detail else PrimaryCategory.INCORRECT_GUESS
    tier = ConfidenceTier.HIGH_CONFIDENCE if is_clear_cut else ConfidenceTier.HEURISTIC_GUIDANCE
    result = ScoredResponse(question_id=question_id, category=category, confidence_tier=tier)
    _apply_overlays(
        result, item, stripped_response, sibling_jurisdiction_items,
        sibling_version_items, tool_call_invoked, language, reasoning_trace,
    )
    return result


def _apply_overlays(
    result: ScoredResponse,
    item: dict,
    stripped_response: str,
    sibling_jurisdiction_items: list[dict] | None,
    sibling_version_items: list[dict] | None,
    tool_call_invoked: bool | None,
    language: str,
    reasoning_trace: str | None = None,
) -> None:
    """Step 7: family-specific overlays, in addition to (never instead of)
    the primary category already assigned above."""
    result.reasoning_trace = reasoning_trace
    family = item.get("family")

    if family == "B":
        result.jurisdiction_adaptation = _score_jurisdiction_adaptation(
            item, stripped_response, sibling_jurisdiction_items or [], language
        )
    if family == "C":
        result.currency_awareness = _score_currency_awareness(
            item, stripped_response, sibling_version_items or [], language
        )
    if item.get("tool_required") == "yes" and tool_call_invoked is not None:
        result.tool_invocation = (
            ToolInvocationCalibration.INVOKED_CORRECTLY if tool_call_invoked
            else ToolInvocationCalibration.UNDER_INVOKED
        )
    elif item.get("tool_required") == "no" and tool_call_invoked:
        result.tool_invocation = ToolInvocationCalibration.OVER_INVOKED


def _score_jurisdiction_adaptation(
    item: dict, stripped_response: str, siblings: list[dict], language: str
) -> JurisdictionAdaptation:
    is_unspecified = not (item.get("jurisdiction") or "").strip()

    if idk_marker_present(stripped_response, language):
        return JurisdictionAdaptation.JURISDICTION_IGNORED

    own_gold = _resolve_gold_text(item)
    if not is_unspecified and own_gold and matches_gold_answer(stripped_response, own_gold):
        return JurisdictionAdaptation.CORRECT_FOR_JURISDICTION

    for sibling in siblings:
        if sibling is item:
            continue
        sibling_gold = _resolve_gold_text(sibling)
        if sibling_gold and matches_gold_answer(stripped_response, sibling_gold):
            # Matches a *different* jurisdiction's answer than the one this
            # item asked about (or, for the unspecified variant, matches one
            # specific jurisdiction's answer when none was asked for at all —
            # H2's predicted default-bias behaviour, 4.2).
            return JurisdictionAdaptation.WRONG_JURISDICTION_DEFAULT

    return JurisdictionAdaptation.JURISDICTION_IGNORED


def _score_currency_awareness(
    item: dict, stripped_response: str, siblings: list[dict], language: str
) -> CurrencyAwareness | None:
    if idk_marker_present(stripped_response, language):
        return CurrencyAwareness.FLAGGED_UNCERTAIN_APPROPRIATELY

    # Every version of a Set C fact shares identical question wording (no
    # "as of <date>" qualifier), so a deterministic model gives the same
    # answer regardless of which version's row happened to be queried —
    # confirmed against a live run (2026-09-12): asked via both the v1 and
    # v2 rows of the same fact, llama3.2:1b gave the same (stale) answer
    # both times. Which version's value the response matches — not which
    # row it was nominally scored against — is what determines
    # Current-vs-Stale; checking only "does this row's OWN value match, but
    # only when this row is itself the current one" left a matched *stale*
    # row's own gold answer uncategorised whenever it wasn't a *different*
    # sibling that happened to be stale. So: check every version (this
    # item's own row, then its siblings) uniformly, and classify by
    # whichever version actually matched.
    for candidate in [item, *[s for s in siblings if s is not item]]:
        candidate_gold = _resolve_gold_text(candidate)
        if candidate_gold and matches_gold_answer(stripped_response, candidate_gold):
            candidate_is_current = not (candidate.get("effective_until") or "").strip()
            return (
                CurrencyAwareness.CURRENT_AND_CORRECT if candidate_is_current
                else CurrencyAwareness.STALE_ASSERTED_AS_CURRENT
            )

    # Doesn't clearly match any known version's value — genuinely wrong
    # rather than confidently stale; not one of this axis's three
    # categories. Left unset (12.3-style: state the gap, don't force a fit).
    return None
