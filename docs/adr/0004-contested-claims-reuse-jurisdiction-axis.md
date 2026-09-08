# 0004. Contested-claims items reuse the Jurisdiction-Adaptation axis

**Status:** Accepted
**Date:** 2026-09-08

## Context

Genuinely contested sovereignty and political-status items (11) initially
appeared to need a new scoring mechanism, since "correctness" for these
items is jurisdiction-relative rather than universal.

## Decision

Reuse the existing Jurisdiction-Adaptation axis (8.3) rather than building
parallel scoring machinery: each item is sourced against every referenced
jurisdiction's own official position (11.3), and a model scores as
Correct-for-Jurisdiction when it reflects the position appropriate to the
stated context — even where two jurisdictions' positions directly
conflict with each other (11.2).

## Consequences

This recovers the field's established consistency-over-correctness
methodology (the BorderLines approach) without adding a bespoke axis
maintained only for this item subset, keeping the rubric surface smaller
and the contested-claims subset auditable using the same mechanism as
every other item family.
