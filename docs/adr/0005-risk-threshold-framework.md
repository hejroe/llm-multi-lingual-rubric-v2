# 0005. RQ5 uses a contextual risk-threshold framework, not a fixed numeric cutoff

**Status:** Accepted
**Date:** 2026-09-08

## Context

A fixed accuracy threshold (e.g. "below X% is high-risk") was considered
for RQ5's risk framing and rejected: both the NIST AI Risk Management
Framework and EU AI Act Article 15 require a documented, context-specific
accuracy level judged by likelihood × severity/impact, not a universal
numeric cutoff.

## Decision

RQ5 adopts the same likelihood × severity/impact judgement structure
(10.6), applied per deployment context, rather than inventing a
percentage this study has no authority to set.

## Consequences

RQ5's output is a documented risk judgement per context, not a single
pass/fail number. This needs to be stated plainly wherever RQ5 results are
reported, so they are not mistaken for a certification threshold.
