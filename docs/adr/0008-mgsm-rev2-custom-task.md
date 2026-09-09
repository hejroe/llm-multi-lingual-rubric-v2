# 0008. Build a custom harness task for MGSM-Rev2 rather than using the stock MGSM task

**Status:** Accepted
**Date:** 2026-09-08

## Context

The Source Register (5.4) vets and includes MGSM-Rev2, excluding the
original MGSM dataset as superseded (known translation errors).
`lm-evaluation-harness`'s built-in `mgsm_direct_*` / `mgsm_cot_native_*`
tasks load from `juletxara/mgsm` — the *original* MGSM dataset, not
MGSM-Rev2. MGSM-Rev2
(`google-research-datasets/MGSM-Rev2` on GitHub) has no existing
lm-evaluation-harness integration; its data ships as per-language TSV
files whose format mirrors the original, per that repository's own
documentation. Running the stock `mgsm` tasks as-is would silently
evaluate against the dataset this project has already excluded.

## Decision

Author a custom lm-evaluation-harness task definition that loads
MGSM-Rev2's TSV files directly, reusing the stock `mgsm` task's structure
(`generate_until`, the same answer-extraction filter, matching prompt
format) since the two datasets share format by design — rather than
either (a) using the stock task and accepting the excluded dataset, or
(b) dropping MGSM-derived math items from Set A/E and relying on
MMLU-ProX alone for cross-lingual coverage.

## Consequences

`configs/lm_eval_tasks/mgsm_rev2/` provides `mgsm_rev2_direct_{de,sw,bn,en}`
task definitions that load the vendored MGSM-Rev2 TSVs, reproducing the
stock `mgsm` task's `generate_until` structure, answer-extraction filter,
and per-language prompt conventions (see that folder's own README for
which conventions were matched, and why). Against a real
lm-evaluation-harness install, all four languages load 250 rows each and
`doc_to_text`/`doc_to_target` render correctly for German and Bengali,
covering both Latin and non-Latin script handling; a `generate_until`
request constructs without error. The full filter/scoring pipeline has
not yet been exercised against a live model backend's actual output, and
Swahili/English have not been independently re-tested (same TSV mechanism
as the tested languages, expected to behave the same) — that end-to-end
check is the pilot's first run against this task, and is treated as
ordinary pre-run verification rather than outstanding engineering (12.8).

Section 3.5's claim that the harness provides "mature task
configurations... for free" holds for MMLU-ProX (9.2) but not for
MGSM-Rev2: the task above is bespoke engineering this project owns and
must maintain.
