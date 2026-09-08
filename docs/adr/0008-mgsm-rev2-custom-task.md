# 0008. Build a custom harness task for MGSM-Rev2 rather than using the stock MGSM task

**Status:** Accepted
**Date:** 2026-09-08

## Context

The Source Register (5.4) vets and includes MGSM-Rev2, excluding the
original MGSM dataset as superseded (known translation errors). Checked
directly against `lm-evaluation-harness`'s own task definitions: the
harness's built-in `mgsm_direct_*` / `mgsm_cot_native_*` tasks load from
`juletxara/mgsm` — the *original* MGSM dataset, not MGSM-Rev2. MGSM-Rev2
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

**Built 2026-09-08** — `configs/lm_eval_tasks/mgsm_rev2/` now provides
`mgsm_rev2_direct_{de,sw,bn,en}` task definitions loading the vendored
MGSM-Rev2 TSVs, with the stock `mgsm` task's `generate_until` structure,
answer-extraction filter, and per-language prompt conventions faithfully
reproduced (that folder's own README documents which conventions were
matched, and why). Verified directly against a real lm-evaluation-harness
install: all four languages load 250 rows each, `doc_to_text`/
`doc_to_target` render correctly (confirmed for German and Bengali,
covering both Latin and non-Latin script handling), and a
`generate_until` request constructs without error. Not yet verified: the
full filter/scoring pipeline against a live model backend's actual output,
and Swahili/English specifically (same TSV mechanism as the two verified
languages, expected to behave identically, but not independently
re-tested) — that end-to-end confirmation is the pilot's first real run
against this task, tracked as ordinary pre-run verification, not as
remaining engineering.

Section 3.5's description of the harness as providing "mature task
configurations... for free" holds for MMLU-ProX (verified compatible,
9.2) but never held for MGSM-Rev2 even after this ADR's decision — the
task above is bespoke engineering this project owns and is now
responsible for maintaining, not something the harness provides. Limitations
12.8 has been updated to reflect this task as built rather than owed.
