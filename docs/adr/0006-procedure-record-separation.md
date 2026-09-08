# 0006. Separate procedure (Section 9) from governed record (Appendix A)

**Status:** Accepted
**Date:** 2026-09-08

## Context

Set E's perturbation method and Set F's conversion lists are each a
method plus the actual data that method produces or consumes. Describing
both in the same place blurs "how this works" with "what is actually in
it," and makes the data record harder to version independently of the
procedure that generates or applies it.

## Decision

The method lives in Section 9 (9.4.1, 9.4.2) alongside a worked good and
bad example each; the actual governed data — conversion lists, perturbation
log, language-aware marker lists (8.6) — lives in Appendix A, versioned
with the corpus (5.8) rather than with the procedure text.

## Consequences

Expanding a conversion list or adding a perturbation-log entry is a data
change (Appendix A, corpus-versioned) and does not require touching
Section 9's procedure text at all, keeping the two kinds of change
independently auditable.
