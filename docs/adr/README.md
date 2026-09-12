# Architecture Decision Records

Each record below captures one significant design decision made during
this study's protocol development: the context that forced a choice, the
decision itself, and its stated consequences. These exist so a reviewer
can find the *why* behind a design choice without re-reading the
Protocol's full prose, and so a later change to that decision has
somewhere concrete to be logged against.

This log is append-only. A superseded decision gets a new ADR that says
so and links back — an existing ADR's Decision/Consequences text is not
edited in place once accepted, matching the amendment discipline used
elsewhere in this project (`STUDY_PROTOCOL.md` Section 13).

| # | Title | Status |
|---|---|---|
| [0001](0001-inference-backend-abstraction.md) | Inference backend abstraction, with Ollama as default | Accepted |
| [0002](0002-statistical-test-selection.md) | Statistical test selection for paired small-sample comparisons | Accepted |
| [0003](0003-starting-scale-not-a-ceiling.md) | Starting scale, not a ceiling | Accepted |
| [0004](0004-contested-claims-reuse-jurisdiction-axis.md) | Contested-claims items reuse the Jurisdiction-Adaptation axis | Accepted |
| [0005](0005-risk-threshold-framework.md) | RQ5 uses a contextual risk-threshold framework, not a fixed numeric cutoff | Accepted |
| [0006](0006-procedure-record-separation.md) | Separate procedure (Section 9) from governed record (Appendix A) | Accepted |
| [0007](0007-tool-calling-simulated-and-live-modes.md) | RQ4 tool-calling supports both simulated and live modes | Accepted |
| [0008](0008-mgsm-rev2-custom-task.md) | Build a custom harness task for MGSM-Rev2 rather than using the stock MGSM task | Accepted |
| [0009](0009-custom-corpus-harness-tasks.md) | Build custom harness tasks reading the curated corpus directly for Sets A, B, C, E, F | Accepted |
| [0010](0010-qwen3-reasoning-mode-both-conditions.md) | Test Qwen3 in both non-reasoning and reasoning mode, as separate conditions | Accepted |
