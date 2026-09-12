# 0009. Build custom harness tasks reading the curated corpus directly for Sets A, B, C, E, F

**Status:** Accepted
**Date:** 2026-09-12

## Context

Building the scoring rubric (Section 8) as code required real
`lm-evaluation-harness` output to design against, so both README smoke
tests were run live for the first time against a local `llama3.2:1b` via
Ollama (`--log_samples`, so per-item raw responses could be inspected).
That run surfaced a gap invisible from reading the Protocol alone: the
stock `mmlu_prox_en_biology` task evaluates the **full upstream MMLU-ProX
biology split** (11,759 items), not the three items curated into
`corpus/vX.Y/set_a.csv`, and its `doc` schema carries the upstream
dataset's own numeric IDs — nothing joins a response back to this
project's own `question_id`. The custom `mgsm_rev2_direct_de` task (ADR
0008) has the identical problem one level down: it vendors and evaluates
the **full 250-row MGSM-Rev2 dataset** per language, not the three
procedural rows curated into Set A. Sets B, C, E, and F — entirely
hand-authored, with no upstream benchmark equivalent — had no harness task
at all. In short: nothing in the project could yet be run scoped to the
specific items this project's own Source Register, Model Register, and
Ethics Register sign-offs actually vetted.

## Decision

Extend ADR 0008's pattern — a task definition that loads this project's
own data directly, rather than an upstream dataset — to every remaining
item family, instead of either (a) running the stock/full-dataset tasks
and post-filtering results down to the curated subset after the fact, or
(b) leaving Sets B, C, E, F unrunnable until a later phase. Each corpus CSV
already carries every field a task needs (`question_id`, `language`,
`gold_answer`, family-specific fields, 5.6); reading it directly via the
harness's own `csv` dataset loader, with a `process_docs` filter (the same
mechanism the stock `mmlu_prox` task itself uses to select a subject,
`lm_eval/tasks/mmlu_prox/en/utils.py`) selecting the right
language/domain/variety cell, keeps the corpus CSVs themselves as the
single source of truth rather than vendoring a further copy.

## Consequences

`configs/lm_eval_tasks/corpus_{a,b,c,e,f}/` provide: `corpus_a_knowledge_*`
and `corpus_a_procedural_*` (4 languages each, Set A's two domains),
`corpus_b_*` and `corpus_c_*` (4 languages each), `corpus_e_en` (English
only, per 5.5/5.8), and `corpus_f_{uk,au}`. Every task's `--log_samples`
output now preserves `doc.question_id`, closing the join-back gap the
stock/mgsm_rev2 tasks had; `scoring/rubric.py` (rubric-v0.3) consumes that
directly, including the sibling-row lookups its Jurisdiction-Adaptation and
Currency-Awareness overlays need (8.3). Each task's own README states what
has and hasn't been independently verified — verification followed this
same ADR's own originating discovery: run it live, inspect the actual
`--log_samples` output, don't assume the YAML is correct because it looks
right.

lm-eval-harness's own `exact_match` metric is retained in every task for
continuity with the rest of the project's tooling, but is explicitly
non-authoritative here: this project's own rubric scores the raw response
text directly (Section 8), and several of these tasks' prompts do not
enforce the letter-extraction convention (`"the answer is (X)"`) the metric
assumes, so its reported accuracy under-counts by design, not by defect.

The stock `mmlu_prox_*` and `mgsm_rev2_direct_*` tasks are not removed —
they remain useful for checking this project's own vetted subset behaves
consistently with the wider benchmark it was drawn from — but are no
longer the mechanism for producing this project's own reportable results.
