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
- **Resolved 2026-09-12/13, and with a consequence not foreseen when this
  ADR was first written.** Investigated live: Ollama's OpenAI-compatible
  endpoint does not honour the native `think` parameter at all (confirmed
  against a real request), so it cannot toggle reasoning mode off — only
  llama.cpp's `chat_template_kwargs: {enable_thinking: false}` (passed
  through the harness's `--gen_kwargs`) actually works. Rather than route
  only the reasoning-mode toggle through llama.cpp while leaving
  everything else on Ollama (which would have meant every Qwen3 run
  used two different backends depending on condition — worse, not
  better), **all** of Qwen3's traffic across every item family — not only
  Set D — was moved to llama.cpp (`scripts/run_pilot_qwen3_llamacpp.sh`),
  for both sizes and both reasoning conditions.
- **New consequence, not previously stated anywhere: Qwen3's results are
  now confounded by backend choice, the same way Set D's results already
  were (ADR 0001), but across every RQ, not only RQ4.** A cross-lingual or
  cross-jurisdiction difference observed for Qwen3 versus, say, Llama
  3.2 or Phi-4-mini could reflect llama.cpp's own sampling/serving-stack
  behaviour rather than a genuine model difference — on top of, not
  instead of, the reasoning-mode difference this ADR already discusses.
  Nothing prior to 2026-09-13 flagged this; it is now recorded here and
  in Limitations 12.11, and Protocol 9.2's Backend Register and 9.3's
  Run Parameter Overrides table are updated to state the backend
  override explicitly rather than leaving it implicit in a script.
  Reasoning-trace capture: llama.cpp does return a separate
  `reasoning_content` field distinct from `content` (confirmed
  2026-09-12), which `scoring/matching.py`'s `<think>`-tag-based
  extraction cannot see — this capture gap is Limitations 12.10's, not
  newly introduced here, but now applies to Qwen3's entire run rather
  than only a hypothetical future Set D task.
