# Pilot Results

**Status:** DRAFT — descriptive results from the first full pilot run, not
a final study report
**Version:** 1.0
**Companion to:** `STUDY_PROTOCOL.md` (Section 10's analysis plan),
corpus-v0.2, rubric-v0.3
**Run completed:** 2026-09-14

This document reports what the first full pilot run actually found, per
Section 10's analysis plan. It does not restate the methodology —
`STUDY_PROTOCOL.md` Section 10 and the RUBRIC_CARDS.md worked examples
remain the authoritative reference for what each test means and why. Every
number below is regenerable from committed code against the raw run data
(Section 11).

## 1. Run Summary

- Corpus v0.2 (`corpus/v0.2/`), all 19 harness tasks (ADR 0009), 228 items
  per model per replicate.
- All 7 registered candidate models (`docs/MODEL_REGISTER.md`), reported
  as **9 conditions** — Qwen3's two sizes each split into non-reasoning
  and reasoning conditions (ADR 0010), which are never pooled.
- 3 replicates each (Protocol 9.3) — 27 total runs.
- **6,156 scored responses** in total.
- Category breakdown (8.2): Incorrect-Guess 3,003 (48.8%), Correct 1,500
  (24.4%), Fabrication 1,209 (19.6%), Infrastructure-Failure 420 (6.8%),
  Correct-Process 24 (0.4%).

## 2. Reliability (10.4)

**100% cross-replicate agreement for every one of the 9 conditions** —
every one of the 228 items received the identical primary category across
all 3 replicates, for every model, on both backends (Ollama and
llama.cpp). At temperature=0 (greedy decoding, Protocol 9.3), this means
no non-determinism was actually observed on this hardware/backend
combination at this pilot's scale — 9.3 already frames non-determinism as
*possible*, not guaranteed, and a clean 100% is a legitimate, reportable
null result on that question, not a sign the replication mechanism failed
to do anything. (A real bug initially made this look like 36.4% agreement
for a single meaningless pooled "llamacpp" entry — Section 6 below.)

## 3. Infrastructure-Failure Rate (10.7) — headline finding

Reported as its own rate, per 10.7, separate from every capability metric
below. Overall 6.8%, but heavily concentrated by model and language, not
evenly spread. Verified directly against the raw harness output that
these are genuine empty completions (`resps: [['']]`), not a text-matching
artifact of the scoring code.

| Model | Overall | bn | sw | de | en |
|---|---|---|---|---|---|
| gemma3n:e2b | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| llama3.2:1b | 1.8% | 0.0% | 0.0% | 7.1% | 0.0% |
| llama3.2:3b | 9.6% | 8.9% | 30.4% | 0.0% | 0.0% |
| phi4-mini | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| qwen3:1.7b (non-reasoning) | 3.5% | 3.6% | 10.7% | 0.0% | 0.0% |
| qwen3:1.7b (reasoning) | 11.0% | 3.6% | 28.6% | 1.8% | 7.1% |
| qwen3:4b (non-reasoning) | 11.0% | 32.1% | 12.5% | 0.0% | 0.0% |
| qwen3:4b (reasoning) | 8.8% | 7.1% | 12.5% | 8.9% | 7.1% |
| smollm2:1.7b | 15.8% | **64.3%** | 0.0% | 0.0% | 0.0% |

`smollm2:1.7b`'s 64.3% Bengali failure rate is the single largest effect
in the entire pilot — consistent with its Model Register entry
("primarily English"), this is exactly the kind of genuine, model-specific
multilingual robustness gap this study exists to surface, distinct from
the scoring-pipeline artefacts (8.5) the original review found. The
`qwen3:4b` non-reasoning-vs-reasoning gap for Bengali (32.1% vs 7.1%) is
worth a targeted follow-up before treating it as a substantive finding
about reasoning mode (Section 10, item 3).

## 4. RQ1 — Cross-lingual correct-rate gap (H1)

Primary comparison per 10.5 (en vs de, procedural domain — the domain
with the larger item count):

| Model | en | de | McNemar p | Corrected verdict |
|---|---|---|---|---|
| gemma3n:e2b | 100.0% | 100.0% | 1.0000 | not significant |
| llama3.2:1b | 100.0% | 33.3% | 0.5000 | not significant |
| llama3.2:3b | 66.7% | 66.7% | 1.0000 | not significant |
| phi4-mini | 100.0% | 100.0% | 1.0000 | not significant |
| qwen3:1.7b (non-reasoning) | 66.7% | 33.3% | 1.0000 | not significant |
| qwen3:1.7b (reasoning) | 66.7% | 66.7% | 1.0000 | not significant |
| qwen3:4b (non-reasoning) | 66.7% | 100.0% | 1.0000 | not significant |
| qwen3:4b (reasoning) | 66.7% | 100.0% | 1.0000 | not significant |
| smollm2:1.7b | 33.3% | 0.0% | 1.0000 | not significant |

Not significant anywhere in the primary confirmatory set. This reflects
the corpus's current scale (n=3 pairs per domain/language) rather than
evidence against H1 — exactly the power limitation Section 12.2
documents, now correctly scoped to the RQs (RQ1/RQ2/RQ6/RQ7) that
actually render a significance verdict.

## 5. RQ2 — Jurisdiction-default bias (H2) — headline finding

**This pilot's strongest confirmed signal.** Primary comparison per 10.5
(German):

| Model | unspecified wrong-default | specified wrong-default | McNemar p | Corrected verdict |
|---|---|---|---|---|
| gemma3n:e2b | 50.0% | 5.0% | 0.0117 | **significant** |
| llama3.2:1b | 80.0% | 10.0% | 0.0001 | **significant** |
| llama3.2:3b | 30.0% | 15.0% | 0.4531 | not significant |
| phi4-mini | 60.0% | 0.0% | 0.0005 | **significant** |
| qwen3:1.7b (non-reasoning) | 30.0% | 10.0% | 0.1250 | not significant |
| qwen3:1.7b (reasoning) | 50.0% | 0.0% | 0.0020 | **significant** |
| qwen3:4b (non-reasoning) | 60.0% | 15.0% | 0.0117 | **significant** |
| qwen3:4b (reasoning) | 60.0% | 5.0% | 0.0010 | **significant** |
| smollm2:1.7b | 30.0% | 5.0% | 0.0625 | not significant |

6 of 9 conditions show a statistically significant tendency to default to
one jurisdiction's answer when none is specified — confirming H2's
predicted direction for most tested models. Not significant for
`llama3.2:3b`, `qwen3:1.7b` (non-reasoning), or `smollm2:1.7b` (the last
two are borderline: p=0.125 and p=0.0625 respectively).

**Notable reasoning-mode contrast (Qwen3-1.7B):** non-reasoning is *not*
significant (p=0.125) but reasoning *is* (p=0.0020) — the opposite of what
ADR 0010 posed as the open question ("does reasoning narrow these error
patterns?"). For Qwen3-4B, both conditions are significant regardless of
reasoning mode. One pilot's worth of data is not enough to call this a
general effect of reasoning mode on jurisdiction bias, but it is a
concrete, specific result worth carrying into a larger run.

## 6. RQ3 — Temporal-currency awareness (H3), descriptive

Per 10.3, reported descriptively (Clopper-Pearson intervals), not as a
significance test — the design already anticipated this pilot's Set C
scale might be underpowered for one.

**`Flagged-Uncertain-Appropriately` is exactly 0.0% (95% CI upper bound
≈1.5%) for every one of the 9 conditions.** No tested model, at any size
or vendor, on either backend, ever expressed appropriate uncertainty about
a stale value instead of confidently asserting or denying it. This is as
clean a confirmation of H3's predicted direction as this descriptive
design can produce.

`Current-and-Correct` ranged 5.0% (`smollm2:1.7b`) to 13.8%
(`llama3.2:3b`) across conditions; `Stale-Asserted-as-Current` ranged
correspondingly. Full per-model intervals are in the regenerated report
(Section 11).

## 7. RQ6 — Contamination check (Set A vs Set E)

**Not available for any model.** Set E currently has only 2 rows total,
both English (`corpus/v0.2/set_e.csv`) — there is no German (primary
language, 10.5) Set E data yet, so no model has a primary-set entry for
RQ6. This is a corpus-coverage gap, not a code or methodology issue (see
Recommendation 1, Section 10).

## 8. RQ7 — Regional variety (US/UK/AU)

n=1 for every one of the 9 conditions (Set F currently has only one item
with a complete US/UK/AU triplet) — the most acutely underpowered RQ in
this pilot, more so than even RQ1. Cochran's Q is 1.0 (no variation
possible from a single item) for every model; no pairwise comparisons
were triggered. Not resolvable at this scale (see Recommendation 1).

## 9. Primary Confirmatory Set (10.5), Summary

Per-model, Holm-Bonferroni-corrected across whichever of RQ1/RQ2/RQ7 had a
primary comparison available (RQ6 unavailable for every model, Section
7):

| Model | RQ1 | RQ2 | RQ7 |
|---|---|---|---|
| gemma3n:e2b | not sig. | **significant** | not sig. |
| llama3.2:1b | not sig. | **significant** | not sig. |
| llama3.2:3b | not sig. | not sig. | not sig. |
| phi4-mini | not sig. | **significant** | not sig. |
| qwen3:1.7b (non-reasoning) | not sig. | not sig. | not sig. |
| qwen3:1.7b (reasoning) | not sig. | **significant** | not sig. |
| qwen3:4b (non-reasoning) | not sig. | **significant** | not sig. |
| qwen3:4b (reasoning) | not sig. | **significant** | not sig. |
| smollm2:1.7b | not sig. | not sig. | not sig. |

## 10. Known Caveats Affecting Interpretation

1. **Qwen3 backend confound (Limitations 12.11).** All four Qwen3
   conditions run on llama.cpp; every other model runs on Ollama. Any
   Qwen3-vs-other-model comparison above could partly reflect
   serving-stack differences rather than genuine model differences, on
   top of the reasoning-mode difference ADR 0010 already isolates.
2. **Statistical power (Limitations 12.2).** RQ1 and RQ7 in particular
   are not resolvable at this corpus scale — their "not significant"
   results should be read as "inconclusive," not "no effect."
3. **Set F rows carry `variety`, not `language`**, in the flat scored-row
   schema, so they fall into a `None` bucket in by-language breakdowns
   (visible as the small `(None,)` groups in the full regenerated
   report). Cosmetic — `scoring.rubric.score_response` already applies
   the correct language fallback internally, so the actual scoring is
   unaffected — but worth fixing so the reporting doesn't need a reader
   to know why (Recommendation 4).
4. This is one pilot run. Per 5.1/5.8, this corpus and model set are a
   starting scale, not a ceiling — every number above should be read as
   "what a first small run found," not a final result.

## 11. Data Provenance and Reproducing This Report

- Raw run data: `results/pilot/` (not tracked in git — `.gitignore`,
  DATA_MANAGEMENT_PLAN.md Section 6).
- Scored data: `results/scored/pilot_all.jsonl` (also not tracked;
  regenerate with:
  ```bash
  python -m scoring.score_pilot_run --pilot-root results/pilot \
      --corpus-version v0.2 --out results/scored/pilot_all.jsonl
  ```
  )
- This report's numbers: `python -m analysis.cli --scored
  results/scored/pilot_all.jsonl`.
- One run directory (`llama3.2_1b/replicate_000`) required manual cleanup
  before scoring — a pre-crash attempt's stale sample files were sitting
  alongside the fresh, complete ones for every task, silently
  double-counting that run until caught by inspection (2026-09-14, git
  history). Moved aside to `results/pilot_stale_backup/`, not deleted.
  `scoring/score_pilot_run.py` now detects and skips this situation
  automatically (Section 10 of this document's companion commit) rather
  than requiring another manual catch.

## 12. Recommended Next Steps

Not yet actioned — listed here so they aren't lost between this pilot and
the next corpus/protocol version (5.8, 7.5):

1. **Expand Set F before RQ7 can say anything.** One triplet (n=1) is the
   single most underpowered comparison in the whole pilot; even a modest
   expansion (5-10 triplets) would let Cochran's Q actually vary.
2. **Add a German Set E row** so RQ6 has a primary-set entry at all — right
   now it's structurally unable to report anything, for any model,
   regardless of corpus scale elsewhere.
3. **Investigate the `qwen3:4b` reasoning-vs-non-reasoning Bengali
   empty-response gap** (32.1% vs 7.1%, Section 3) specifically before
   treating it as a substantive finding — could be a real reasoning-mode
   effect, or an artifact of llama.cpp's chat-template handling for
   non-Latin scripts when `enable_thinking: false` is set. A small,
   targeted set of manual queries against both conditions would settle
   this cheaply.
4. **Fix Set F's language-field gap** (Section 10, item 3) — populate
   `language` (not just `variety`) on Set F rows so by-language
   breakdowns don't need a footnote to explain a `None` bucket.
5. **Reconsider replication count in light of 100% reliability
   (Section 2).** Either this pilot's hardware/backend combination is
   genuinely fully deterministic at this scale (in which case 3
   replicates may be more than needed going forward, freeing up run
   budget elsewhere), or a larger, more diverse run would find the
   non-determinism 9.3 anticipates. Worth deciding deliberately rather
   than defaulting to 3 again without re-examining it.
6. **Bound the Qwen3 backend confound (Caveat 1) rather than only
   disclosing it** — e.g. a small comparison arm running one non-Qwen3
   model through llama.cpp too, to see how much of any observed
   Qwen3-vs-rest difference is attributable to backend alone.
