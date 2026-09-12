# 0010. Test Qwen3 in both non-reasoning and reasoning mode, as separate conditions

**Status:** Accepted
**Date:** 2026-09-12

## Context

Protocol 9.3's Run Parameter Overrides table set Qwen3 (all sizes) to
non-reasoning ("dialogue") mode by default, reasoning that using reasoning
mode uniformly would confound RQ1-style cross-model comparisons with a
mode choice rather than a genuine capability difference. That entry was
explicitly "flagged for revisiting once Section 10's analysis plan is
written" — which it now has been (the `analysis/` pipeline). Separately,
live verification of the llama.cpp/Set D path (2026-09-12, Limitations
12.10) showed Qwen3 4B defaults to reasoning ("thinking") mode unless
explicitly suppressed — i.e. non-reasoning mode is itself an artificial
restriction away from how this model actually ships and is actually used
by anyone deploying it with its own defaults. Testing only the suppressed
mode risks understating real-world behaviour and misses a genuinely
interesting question this pilot's design is well-placed to answer: does
reasoning narrow the cross-lingual gap (RQ1), the jurisdiction-default
bias (RQ2), the stale-answer rate (RQ3), or tool-invocation calibration
(RQ4)?

## Decision

Keep non-reasoning mode as Qwen3's *primary, pre-registered* condition for
every confirmatory RQ (RQ1, RQ2, RQ3, RQ6, RQ7) — this is what keeps Qwen3
comparable to every other tested model under the same fixed run
parameters (9.3), which is the whole point of fixing temperature and
decoding uniformly in the first place. Additionally run Qwen3 in reasoning
mode as a second, explicit, labelled condition, reported descriptively
alongside the primary comparison rather than pooled into it — the same
pattern ADR 0007 already established for Set D's Simulated/Live tool
modes: one mode is the controlled baseline, the other is a genuinely
useful complementary condition, not a replacement.

This is ordinary pre-freeze drafting, not a logged amendment (Section 13)
— the Protocol remains DRAFT, and 9.3's own override table already
flagged this specific choice as provisional.

## Consequences

- Protocol 9.3's override table updated: Qwen3 runs both modes; the
  non-reasoning condition alone is what every confirmatory RQ's primary,
  pre-registered comparison uses.
- 9.6 run-level provenance gains a `reasoning_mode` field
  (`scoring/io.py`'s `RunProvenance.reasoning_mode`), so reasoning- and
  non-reasoning-mode results are never silently pooled.
- Roughly doubles Qwen3's run volume (2 sizes × 2 modes instead of 2 sizes
  × 1) — a bounded, deliberate cost specific to one model family, not a
  combinatorial expansion of the whole design.
- Not yet resolved, deferred to whenever Set D's own harness task is
  built: exactly how reasoning mode gets toggled per backend (a Qwen3
  chat-template parameter such as `enable_thinking`, passed through
  whatever mechanism the harness's `model_args` or a custom wrapper
  supports), and whether the reasoning trace arrives in a separate
  `reasoning_content` field (as seen from llama.cpp, 2026-09-12) or
  embedded in `content` behind `<think>` tags (as Ollama's chat template
  may do instead) — the latter is exactly the leakage pattern 8.4 step 2
  already strips, but confirming which backend does which, empirically,
  remains open work.
