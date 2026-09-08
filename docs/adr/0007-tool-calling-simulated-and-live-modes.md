# 0007. RQ4 tool-calling supports both simulated and live modes

**Status:** Accepted
**Date:** 2026-09-08

## Context

Tool-Invocation Calibration (RQ4, 8.3) can be tested either against a
controlled, captured tool response (repeatable, no external dependency) or
against a live tool call against real data (higher ecological validity,
but non-repeatable and dependent on external services).

## Decision

Support both modes (9.5). Simulated mode is the default, for repeatable,
controlled testing of a model's response to a specific tool result. Live
mode is offered as a genuinely useful complementary option, not a
replacement, for cases where behaviour against real, uncontrolled data is
itself the thing being studied.

## Consequences

Any result drawing on live-mode runs must record that the tool response
was not captured or frozen (9.6 provenance), since it cannot be exactly
reproduced later. Simulated- and live-mode results are not directly
poolable without saying so.
