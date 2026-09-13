"""Category vocabulary for the scoring rubric (STUDY_PROTOCOL.md Section 8).

rubric-v0.3 (docs/STUDY_PROTOCOL.md 8.8). This module carries no logic —
just the fixed vocabulary the decision logic in `rubric.py` assigns from.
"""

from enum import Enum


class PrimaryCategory(str, Enum):
    """8.2 — every response gets exactly one of these."""

    INFRASTRUCTURE_FAILURE = "Infrastructure-Failure"
    CORRECT = "Correct"
    CORRECT_PROCESS = "Correct-Process"
    IDK = "IDK"
    INCORRECT_GUESS = "Incorrect-Guess"
    FABRICATION = "Fabrication"


class ConfidenceTier(str, Enum):
    """8.7 — carried alongside a category assigned at steps 4, 5, or 6.

    Steps 1 and 3 are High-Confidence only, by construction — mechanical
    tests with no ambiguous branch, so the tier is not a free choice
    there. Step 5 (Correct-Process) is *always* Heuristic-Guidance, not
    just sometimes: the corpus carries no gold *method* annotation per
    procedural item (only the final gold_answer), so "a valid method was
    shown" is a best-effort proxy (shown-working detected) every time, not
    a mechanical certainty in some cases and a judgement call in others
    the way steps 4 and 6 are (corrected 2026-09-13 — this previously said
    step 5 was High-Confidence-only, contradicting both the Protocol text
    it was meant to mirror and `scoring/rubric.py`'s own actual behaviour).
    """

    HIGH_CONFIDENCE = "High-Confidence"
    HEURISTIC_GUIDANCE = "Heuristic-Guidance"


class JurisdictionAdaptation(str, Enum):
    """8.3 overlay — Set B (RQ2)."""

    CORRECT_FOR_JURISDICTION = "Correct-for-Jurisdiction"
    WRONG_JURISDICTION_DEFAULT = "Wrong-Jurisdiction-Default"
    JURISDICTION_IGNORED = "Jurisdiction-Ignored"
    REFUSED = "Refused"  # 11.5 sub-tag of Jurisdiction-Ignored


class CurrencyAwareness(str, Enum):
    """8.3 overlay — Set C (RQ3)."""

    CURRENT_AND_CORRECT = "Current-and-Correct"
    STALE_ASSERTED_AS_CURRENT = "Stale-Asserted-as-Current"
    FLAGGED_UNCERTAIN_APPROPRIATELY = "Flagged-Uncertain-Appropriately"


class ToolInvocationCalibration(str, Enum):
    """8.3 overlay — Set D (RQ4, `tool_required` re-tagging, 5.5)."""

    INVOKED_CORRECTLY = "Invoked-Correctly"
    OVER_INVOKED = "Over-Invoked"
    UNDER_INVOKED = "Under-Invoked"
