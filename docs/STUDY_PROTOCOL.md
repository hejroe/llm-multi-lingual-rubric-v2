# Study Protocol

**Version:** 0.29 (DRAFT — not frozen; section 1 pending, deferred by request)
**Status:** DRAFT
**Last updated:** 2026-09-16

Amendments after freeze are logged in Section 13.

---

## 2. Research Questions

This section sets out the questions the pilot is designed to answer. RQ1,
RQ2, RQ3, RQ6, RQ7 and RQ8 are confirmatory (tested against pre-specified
criteria, per the amendment rules in Section 13); RQ4 is exploratory; RQ5 is
a framing question that interprets the others against a named
professional-use context rather than testing a hypothesis of its own.
Results across all eight are reported per model using a common method set
out in Section 10.

RQ1 (confirmatory). For culturally/linguistically neutral factual and
procedural content, does answer correctness/consistency differ across
languages once scoring-pipeline artefacts (English-only regex matching,
chain-of-thought leakage, error-as-neutral-zero) are removed?

RQ2 (confirmatory). For facts whose correct value is jurisdiction-contingent
(legal ownership/status questions, regulatory thresholds, professional-conduct
norms), does the model give the jurisdictionally correct answer when a
jurisdiction is specified, and does it default to one jurisdiction's answer
when none is specified?

RQ3 (confirmatory). For facts with a known change cadence (tax-year figures,
statute amendments), does the model's answer reflect awareness of its own
knowledge-cutoff limits, versus confidently asserting a stale value as
current?

RQ4 (exploratory). When given a search/retrieval tool, does the model
correctly decide *when* to invoke it (calibration, not just capability), and
does providing that tool measurably reduce RQ2/RQ3-type errors?

RQ5 (framing question). Do the error rates and modes observed under
RQ1-RQ4 and RQ7 exceed a stated risk threshold for a named professional-use
context (e.g. UK small-practice accounting guidance, general
legal-information triage) — producing an evidence-based viability judgement
rather than a bare accuracy score?

RQ6 (confirmatory). Does a model's measured performance on paraphrased or
perturbed versions of a benchmark item (Set E) degrade relative to its own
measured performance on the unperturbed original (Set A), within this
pilot — indicating possible train-test contamination or shallow
pattern-matching rather than the claimed capability? This compares a model
against itself; no externally published score is retrieved or used (see
H6, 4.2, and 10.3).

RQ7 (confirmatory). Does model performance differ systematically between
major regional varieties of the same language (US, UK, and Australian
English) in spelling, units, terminology and idiom, indicating training-data
representation bias toward one variety rather than genuine task difficulty?

RQ8 (confirmatory, added 2026-09-19). For a fixed model answering a fixed
corpus item under identical prompt and generation parameters, does the
choice of serving harness/backend (e.g. Ollama vs. llama.cpp) change the
model's measured behaviour — its primary response category (8.2) or its
Infrastructure-Failure rate (10.7) — independent of any of RQ1-RQ7's own
manipulations? This treats backend/harness choice as a genuine deployment
variable in its own right, not only a methodological confound to disclose
(as Limitations 12.11/12.12 originally did): an AI user deploying a given
model makes a real choice of serving stack, and a harness's own design
decisions — which parameters it exposes, how it parses model output — can
constrain or change what behaviour that choice actually produces. Motivated
directly by two pieces of evidence this pilot already produced rather than
a hypothetical concern: a harness-specific parser crash that blocked one
model/condition entirely (12.12), and a measured Infrastructure-Failure
rate difference between Qwen3's reasoning and non-reasoning conditions on
the same backend, suggestive of harness-level fragility under certain
response shapes.

---

## 3. Background & Prior Work

### 3.1 Purpose and Scope

This section situates the pilot within the review that prompted it and the
existing literature, so design choices elsewhere in this document
(building on lm-evaluation-harness, the source exclusions in 5.4, the
RQ5 framework in 10.6) are traceable to a specific finding or gap, not
asserted without support.

### 3.2 The Original Pre-Print and This Review's Findings

The pre-print ("The Leaderboard Illusion: A Risk Analysis of Performance
Degradation in Multilingual Large Language Models," hejroe/llm-multi-lingual-rubric)
reported a catastrophic cross-lingual performance collapse on Factual
Accuracy items — apparent drift of roughly 40-47 percentage points between
English and German/Spanish for most tested models. A methodological review
of the repository's own raw experimental data (without modifying the
published repository) identified three specific scoring-pipeline bugs: an
English-only answer-matching regex applied to non-English responses;
unstripped chain-of-thought (`<think>`) blocks being scored as if they
were the final answer; and API/infrastructure errors being scored as a
neutral zero alongside genuine wrong answers rather than excluded.
Correcting these three issues against the same raw data reduced the
apparent drift to roughly 4-6 percentage points for most models, and
revealed that the one model which had appeared immune to the collapse
(qwen3:8b) was itself an artefact of the think-block leakage bug, not
genuine robustness. This finding is the direct origin of the rubric's
Infrastructure-Failure category and its decision-ordering (8.2, 8.4), and
motivated redesigning the corpus around professionally translated
existing benchmarks (Set A, 5.5) rather than the original repo's DIY
machine-translated approach.

### 3.3 Related Work in Multilingual/Cross-Lingual Evaluation

MMLU-ProX and MGSM(-Rev2) provide professionally translated, parallel-item
multilingual benchmarks and were adopted as Set A's source (5.4) precisely
because they avoid the translation-fidelity problem the original repo's
DIY approach exposed. The paper introducing MGSM-Rev2 is itself directly
relevant to this project's own founding premise: it found that MGSM's
apparent 15-17-percentage-point cross-lingual gap was largely an artefact
of translation errors and language-naive answer-extraction (e.g. French's
comma decimal separator being misread by an English-oriented regex), and
shrank to 1-2 points once corrected — independent corroboration, on a
different benchmark, of the same scoring-artefact-vs-genuine-gap distinction
this study's original review found in the "Leaderboard Illusion" pre-print. IrokoBench/AfriMGSM extends this to African
languages under a clean licence (Apache-2.0) but was found, on checking,
not to be strictly necessary for this pilot's language set once
MGSM-Rev2's own coverage was confirmed (6.3). A distinction raised early
in this project's design — between raw data scarcity for a language and
genuine lexical/cultural gaps in what a language has words for at all —
maps to the resource-level vs. cultural-groundedness distinction
documented in the MELLA literature, and informed treating resource level
and script as separate selection criteria (6.2) rather than a single
"high/low-resource" axis.

### 3.4 Related Work in Jurisdiction- and Domain-Specific Evaluation

BorderLines (Li, Haider, Callison-Burch, NAACL 2024) established the
consistency-over-correctness methodology this study's contested-claims
handling is built on (11.2) — a model's answer compared across
jurisdictional framings rather than scored against one universal gold
answer. Its own dataset was checked and excluded from this study (5.4) for
lacking a stated licence, not for any methodological flaw; the method was
adopted, the specific dataset was not. LegalBench and Legal RAG Bench were
checked for RQ2 and found to test legal reasoning and RAG-grounded legal
question-answering respectively, but neither tests cross-jurisdiction
consistency for the same underlying fact, confirming this remains a
genuine gap rather than a solved problem being re-done. For RQ5's
risk-threshold framework, the NIST AI Risk Management Framework and
Article 15 of the EU AI Act both require (10.6) a documented,
context-specific accuracy level judged by likelihood and severity, not a
fixed numeric threshold — the framework adopted in 10.6 follows this same
approach rather than inventing a percentage.

### 3.5 Positioning This Study

Rather than building bespoke evaluation tooling, this pilot runs on
EleutherAI's lm-evaluation-harness, which implements a mature task
configuration for MMLU-ProX (9.2) and supports Ollama and other backends
via an OpenAI-compatible API (9.2), and allows a custom rubric to sit
alongside its existing scoring via configurable task definitions, so
others can define their own rubrics on the same infrastructure rather
than a closed, one-off scoring script. The harness's *built-in* MGSM task
does not cover MGSM-Rev2, however: a custom task definition was required
and has been built (9.2, ADR 0008) — genuine engineering this project
owns, not something the harness provides for free. This study's
contribution is not a new evaluation harness, but a rubric and corpus
design (Sections 5, 8) that tests jurisdiction-, currency-,
tool-calibration- and variety-based consistency — axes the existing
literature (3.3, 3.4) does not currently cover together in one design.

---

## 4. Hypotheses

### 4.1 Purpose and Scope

A specific, falsifiable, directional hypothesis for each confirmatory
research question (RQ1, RQ2, RQ3, RQ6, RQ7, RQ8), grounded in the rubric
categories (Section 8) and the analysis thresholds already fixed in 10.3 —
not a restatement of the research question, but a prediction with a stated
direction and a stated observation that would refute it. RQ4 (exploratory)
and RQ5 (framing) deliberately get no formal hypothesis here: stating one
for either would dress up an open question as a confirmatory test, which
Section 2 explicitly says they are not. A refuted hypothesis is a valid,
reportable outcome of this pilot — it is logged as a finding, not reworded
or quietly dropped after the fact.

### 4.2 Hypotheses per Confirmatory RQ

**H1 (RQ1).** Once the three scoring-pipeline artefacts identified in the
original review are corrected (8.5), the Correct-rate gap between English
and each tested language on neutral content (Set A) will be small —
directionally near zero — rather than the 40+ percentage-point gaps the
uncorrected scoring produced. Refuted by: a persistently large gap after
correction, which would point to a genuine capability difference rather
than a scoring artefact.

**H2 (RQ2).** Models will default to one jurisdiction's answer when none
is specified (rather than declining to answer or presenting multiple
jurisdictions' positions), and specifying the jurisdiction explicitly will
improve correctness but not fully close the gap to the H1 baseline.
Refuted by: no consistent default pattern, or full correctness regardless
of whether a jurisdiction is specified.

**H3 (RQ3).** Models will disproportionately produce
Stale-Asserted-as-Current responses rather than
Flagged-Uncertain-Appropriately ones for temporal-currency items (Set C) —
i.e. models will tend to assert a frozen-training-data value as current
rather than expressing appropriate uncertainty about its currency. Refuted
by: a rate favouring appropriate uncertainty over confident staleness.

**H6 (RQ6).** At least some models will show a measurable Correct-rate
drop on perturbed items (Set E) relative to their Set A originals, and the
size of that drop will vary by model — consistent with some degree of
train-test memorisation rather than uniformly generalised capability.
Refuted by: uniformly negligible drop across every tested model.

**H7 (RQ7).** UK-English and Australian-English items (Set F) will show a
lower Correct-rate than their US-English originals for at least some
models; a similarly sized drop for both varieties points to a general
non-US training-data bias rather than a UK-specific one, per the three-way
test design in 10.3. Refuted by: no drop for either variety.

**H8 (RQ8, added 2026-09-19).** At least one tested model will show a
measurably different primary-category distribution (8.2) or
Infrastructure-Failure rate (10.7) for the same item, under identical
prompt and generation parameters, when served through a different
backend — consistent with harness/serving-stack choice being a genuine,
measurable source of behavioural variation, not merely a theoretical risk
to disclose. Refuted by: no primary-category or Infrastructure-Failure-
rate difference, for any tested model, between backends.

### 4.3 RQ4 and RQ5

Neither is hypothesis-bearing. RQ4 carries a stated descriptive
expectation only — models more often under-invoke than over-invoke a
tool, consistent with H3's prediction of overconfidence — clearly labelled
as non-confirmatory framing, not a test to be passed or failed. RQ5 is a
downstream interpretive judgement built from the other RQs' results
(10.6), not a hypothesis of its own.

### 4.4 Freeze and Amendment

These hypotheses are part of what gets fixed before the pilot runs, per
this document's header. Any change to a stated hypothesis after that point
is logged in Section 13 as an amendment.

---

## 5. Corpus

### 5.1 Purpose and Scope

This section defines the test corpus: how candidate sources are found, how
they are checked before use, how that checking is recorded, what the
resulting item families contain, the data each item carries, and how the
corpus is versioned as it grows.

Initial work uses small, validated sets sized to build and test the
methodology across each item family. This is a starting point for
development, not a ceiling: the corpus structure does not cap scale, and
running any family at its full available size is expected use, not a
special case requiring a different mechanism.

### 5.2 Source Discovery

Candidate sources are identified through: literature review of existing
multilingual and domain benchmarks (building on the related work already
surveyed — MMLU-ProX, MGSM, BorderLines, IrokoBench/AfriMGSM); benchmark and
dataset registries (e.g. Hugging Face Datasets, Papers with Code); and, for
jurisdiction- and time-dependent items (Sets B and C), primary legal and
regulatory sources (statutes, treaties, government guidance) rather than
secondary summaries.

Every candidate identified this way is passed to source vetting (5.3) before
any item is drawn from it; discovery does not itself constitute inclusion.

### 5.3 Source Vetting Criteria

Before any benchmark or source contributes items to Sets A or E, it is
checked against:

1. **Ownership and provenance.** Who holds the rights to the data, and is
   that provenance clear and verifiable — as distinct from what licence is
   merely stated. A stated licence is only as reliable as the rights of the
   party granting it; where a source's chain of ownership is unclear or
   disputed, it is excluded regardless of its stated terms.
2. **Licence compatibility.** The stated licence permits commercial
   derivative use; non-commercial-only and share-alike-incompatible licences
   are excluded.
3. **Known contamination or quality issues.** Checked against current
   contamination-detection literature, not assumed clean.
4. **Currency.** The source is actively maintained, not a deprecated or
   superseded release.

This check is dated at the time it is performed and is re-run before any
corpus version bump, since ownership disputes, licence terms, and
maintenance status can all change after a source was first vetted.

### 5.4 Source Register

Every source considered — included or excluded — is logged here, together
with the outcome of 5.3 and the reasoning behind the decision. This is the
exclusion log.

| Source | Version / snapshot date | Ownership/provenance check | Licence | Contamination/quality check | Currency check | Decision | Reasoning |
|---|---|---|---|---|---|---|---|
| MMLU-Pro (TIGER-Lab) | HF release, accessed 2026-09-03 | Clear — TIGER-Lab, NeurIPS 2024 paper | MIT | Designed to reduce contamination vs. original MMLU (harder distractors); no independent RQ6-style check yet performed | Actively maintained, live leaderboard | Included (Sets A/E) | Clear ownership, permissive licence, no share-alike obligation |
| MGSM-Rev2 (Google Research) | GitHub release, accessed 2026-09-03 | Clear — Google Research; corrected/retranslated successor to original MGSM, itself built on GSM8K (OpenAI, MIT) | CC BY-SA 4.0 | Not yet independently checked; supersedes original MGSM's known translation errors | Actively maintained; explicit drop-in replacement for original MGSM | Included (Sets A/E) | Commercial use permitted; its share-alike obligation for any derivative applies to Set E/F items built from it. Corrected 2026-09-16 (12.9): the project's general CC BY 4.0 publication does not discharge this obligation — no current Set E/F item is actually affected (all derive from the MIT-licensed MMLU-ProX side of Set A instead), but the vendored TSVs themselves still need a BY-SA notice, and any future MGSM-Rev2-derived item must carry CC BY-SA 4.0 specifically |
| Original MGSM (Google Research / Surge AI) | url-nlp repo | Mixed — GSM8K base (OpenAI, MIT) plus a separately licensed translation layer | CC BY-SA 4.0 / MIT (mixed) | Known translation errors, corrected in Rev2 | Superseded by MGSM-Rev2 | Excluded — superseded | Use MGSM-Rev2 instead; retained here only as an audit note |
| AfriMGSM / IrokoBench (Masakhane) | HF release, accessed 2026-09-03 | Clear — Masakhane NLP, named maintainer contact | Apache-2.0 | Not yet independently checked | Actively maintained (ongoing Masakhane project) | Included, not currently drawn on | Passed vetting and remains available for a later language expansion, but 3.3's own account found it was not strictly necessary for this pilot's language set once MGSM-Rev2's coverage was confirmed (6.3) — no corpus item currently sources from it; corrected 2026-09-16 to match 3.3 rather than reading as a used-but-unlogged source |
| BorderLines (Li, Haider, Callison-Burch — NAACL 2024) | GitHub repo, accessed 2026-09-03 | Unclear — no LICENSE file found in the repository | None stated | Not checked — blocked by the licence gap | N/A | Excluded (pending) | No licence found; absent one, default copyright grants no reuse rights. Not to be used until the authors confirm terms in writing — this is the case 5.3's ownership/provenance check exists to catch |
| MMLU-ProX (li-lab) | HF release, accessed 2026-09-03 | Clear — li-lab, EMNLP 2025 paper; distinct organisation from MMLU-Pro/TIGER-Lab | MIT | Not yet independently checked | Actively maintained, recent (2025) release | Included (Sets A/E) | Clear ownership, permissive licence, no share-alike obligation; covers all Section 6 candidate languages |

*Licence readings above are a preliminary technical check, not legal advice; each "included" decision still requires confirmation before Set E or Set F derivative generation begins.*

### 5.5 Item Families

**A — Neutral Multilingual Core** (RQ1). Drawn from existing professionally
translated public benchmarks (MMLU-ProX subset, MGSM-Rev2 subset) that have
passed source vetting, rather than newly authored translations — avoiding
the original repo's DIY-translation problem.

**B — Jurisdiction-Contingent Set** (RQ2, tagged for RQ5). Hand-authored.
Each fact has one unspecified-jurisdiction variant (tests default bias) and
N jurisdiction-specified variants (tests correct adaptation). Every item
requires a citable primary source (statute, treaty, government guidance).
Symmetric by design: claims cutting against the UK's position are included
alongside ones favouring it. Sits behind the Ethics Register sign-off gate.
The unspecified-jurisdiction variant carries no `gold_answer` (5.6) —
8.2's Correct/Incorrect axis is not scored for it, since nominating any
single jurisdiction's answer as "correct" for this variant would itself
introduce the exact default bias this variant exists to test. Only the 8.3
Jurisdiction-Adaptation overlay (Wrong-Jurisdiction-Default /
Jurisdiction-Ignored) is scored for it. Jurisdiction-specified variants
carry their own jurisdiction's `gold_answer` as normal and are scored on
both axes.

**C — Temporal-Currency Set** (RQ3). Hand-authored. Each item has an
effective-from/until date and a versioned gold answer. Maintenance cadence
for re-checking gold answers against source is defined in the Data
Management Plan.

**D — Tool-Necessity Mixed Set** (RQ4). Not a separate family of items —
a re-tagging. A `tool_required: yes/no` label (5.6) is added directly to
the existing row for a sampled item from Set B, Set C, or Set A, rather
than duplicating that item under a fourth family value; the item's
`family` field (5.6) stays A, B, or C. Whether an item is "in Set D" is
therefore a property checked at analysis time (does it carry a
`tool_required` label? — 8.4 step 7), not a family of its own, scoring
whether the model's own decision to invoke search matches the label,
independent of answer correctness.

**E — Contamination-Check Set** (RQ6). Paraphrased/perturbed twins of a
sample of Set A items, run alongside their originals, generated using a
documented, reproducible perturbation method. The method is described in
Section 9; the perturbation log itself (which item, what changed, when) is
recorded in Appendix A, kept separate from the procedure that governs it.
Subject to the same source vetting as the items they are derived from.

**F — Regional Variety Set** (RQ7). UK-English and Australian-English twins
of a sample of Set A English items, generated via a documented, reproducible
substitution method: a maintained conversion list per variety (spelling,
units, terminology). The method — including the authoritative style
references each list is sourced from (e.g. a recognised UK/US usage guide;
the relevant Australian government style manual), so the transformation
does not itself encode our own assumptions about what counts as "UK" or
"Australian" English — is described in Section 9; the conversion lists
themselves are recorded in Appendix A, kept separate from the procedure
that governs them. Restricted to items whose underlying content is
jurisdiction-neutral: Set F tests surface-form bias only, and must not draw
on items whose correct answer is itself jurisdiction-contingent — that risk
belongs to Set B (RQ2), and conflating the two would undermine both. Run
alongside the US-English originals. Generated by us, not sourced, since the
vetted sources default to US-English; subject to the same licence/provenance
discipline as Set E, being derivatives of MMLU-ProX/MGSM-Rev2 items.

### 5.6 Common Item Schema

Every item, in every family, carries: `question_id`, `family`, `domain`,
`source_citation`, `source_snapshot_date`, `licence`, `gold_answer` (null
for Set B's unspecified-jurisdiction variant specifically, per 5.5 — every
other item carries a value), `language_variant_of`. Family-specific fields
extend this: `jurisdiction` (Set B), `effective_from`/`effective_until`
(Set C), `tool_required` (added to a sampled subset of Sets A, B, C per
5.5 — not itself a family value), `variety` and `conversion_list_version`
(Set F).

### 5.7 Provenance and Temporal Metadata

Item-level: each item records the snapshot date/version of its source
(e.g. "MMLU-ProX, release X, accessed 2026-09-03").

Run-level: every experimental run stamps corpus version, model digest, and
run timestamp together, so a result is only ever interpreted pinned to a
specific corpus version against a specific model digest on a specific date.

### 5.8 Versioning and Scale

Each corpus release is versioned (`corpus-vX.Y`). Expanding an item family's
coverage, or running it at full scale, produces a new version; it never
edits an existing one, so any published result continues to cite the exact
version it was measured against. The initial small validated sets are
corpus-v0.1; nothing in the schema or the family definitions restricts a
later version from covering a source's full item set.

**corpus-v0.1 exists** (`corpus/v0.1/`, built 2026-09-08): 24 Set A rows (3
MMLU-ProX biology items + 3 MGSM-Rev2 items, each across en/de/sw/bn,
`tool_required` tagged on two of the six), 2 Set E rows (reviewed and
accepted by the study owner 2026-09-09, 9.4.1, Appendix A.4), and 2 Set F
rows (one item, UK/AU varieties). Its original 1-fact Set B/C content has
been superseded by corpus-v0.2 below; v0.1 itself is unchanged and remains
a valid citable snapshot.

**corpus-v0.2 exists** (`corpus/v0.2/`, built 2026-09-09): supersedes
v0.1's Set B and Set C only (5.8's versioning rule — expand, don't edit).
Set A, Set E and Set F are carried forward unchanged. Set B is now 10
jurisdiction-contingent facts (120 rows: unspecified + 2 jurisdiction
variants, each across en/de/sw/bn), every fact independently verified
against a primary source and logged in the Ethics Register (11.4,
signed off by the study owner, hejroe, 2026-09-09). Set C is now 10
temporal-currency facts (80 rows: 2 versions each, across en/de/sw/bn),
each with a clean single-variable change and a verified effective date.
The German/Swahili/Bengali translations of both families were
machine-drafted and have since been reviewed by the study owner
(2026-09-11); they carry `review_status: translation-reviewed`
accordingly (the same review applied to Appendix A.3's hand-authored
non-English content, A.3). Ten facts per family is sized to let
McNemar's exact test and the Clopper-Pearson interval actually run on a
non-degenerate sample, not to give RQ2/RQ3 full statistical power — 12.2's
power limitation is unchanged by this release (`corpus/v0.2/README.md`
has the full reasoning and per-fact source table).

**corpus-v0.3 exists** (`corpus/v0.3/`, built 2026-09-15): expands Set A,
Set B, Set E and Set F, directly motivated by the first full pilot run's
own findings (`docs/PILOT_RESULTS.md` Section 12) — RQ1 was
mathematically incapable of significance at its previous scale (3 paired
items; McNemar's exact test on ≤3 discordant pairs cannot reach p<0.05
regardless of true effect size), RQ7 had only one triplet, and RQ6 had no
German (primary-language) data at all. Set C is carried forward
unchanged (the same treatment Set A/E/F received in v0.2, mirrored here).

- **Set A**: knowledge domain grown from 3 to 39 items per language, and
  procedural domain from 3 to 23, by sampling further already-vetted
  MMLU-ProX (biology category, HF datasets-server API) and MGSM-Rev2
  rows (already vendored in this repository, 250/language, only 3
  previously used) — no new source vetting needed, since both were
  already vetted (5.4) for v0.1.
- **Set F**: grown from 1 to 21 US/UK/AU triplets, generated from the
  newly added Set A knowledge items via the same documented
  conversion-list method (9.4.2). Appendix A.2's conversion list itself
  was expanded (17 more word pairs, same categories, same cited sources
  — Wikipedia's spelling-differences article, Oxford Reference, the
  Australian Government Style Manual) since the original 9-word list
  rarely matched real MCQ text; several well-known but genuinely
  context-dependent pairs (program/programme, practice/practise,
  license/licence, check/cheque, curb/kerb) were deliberately excluded,
  same reasoning as the existing "public school" exclusion.
- **Set E**: grown from 2 to 12 items, including 5 in German — the
  single change that actually unblocks RQ6, which previously had zero
  primary-language data to report against, for any model, regardless of
  scale elsewhere. A new `corpus_e_de` harness task was added alongside
  the existing `corpus_e_en`.
- **Set B**: grown from 10 to 16 facts (192 rows), each of the 6 new
  facts genuinely researched against a primary source via web search
  (5.3's discipline), logged in the Ethics Register (11.4).

Every new item across all four families was drafted as
`review_status: candidate` (Set B/E), pending the study owner's sign-off
per 5.3/9.4.1/11.4 rather than self-certified by the drafting process —
that review has since been completed (hejroe, 2026-09-15: reviewed all
changes, "paying special attention to the new items," no amendments),
and `review_status` and the Ethics Register sign-off column below both
reflect that sign-off, not the pending state this paragraph originally
described at authoring time.

**corpus-v0.4 exists** (`corpus/v0.4/`, built 2026-09-16): expands Set E
only, directly motivated by a review finding that RQ6-DE's McNemar test
remained mathematically incapable of significance even after `v0.3` —
5 German items gives a best-case floor of `2*(0.5)^5=0.0625`, still above
0.05; `n>=6` is the bare minimum. Set E grows from 12 to 26 rows (7 new
facts x en/de, drawn from previously-unused Set A knowledge items),
bringing the German count to 12. Set A, Set B and Set C are carried
forward unchanged; Set F is carried forward with one disclosed
correctness fix (`F-KNOW-10`'s unconverted "catalyze," a gap in the
`-ize/-ise` mechanism that a `-yze/-yse` word falls outside of — the
`v0.3` copy is left as published, since a pilot run was already using it
at the time this was found; `corpus/v0.4/README.md` has the full
reasoning). Every new Set E row was drafted as `review_status: candidate`,
reviewed and accepted by the study owner 2026-09-19 (Appendix A.4 has the
per-item detail) — usable as confirmatory RQ6-DE evidence per this
section's own established discipline. A native-reader check of the
existing 21 Set F triplets was also completed by the study owner on the
same date, closing the sensitivity-validation gap Appendix A.2 had left
open (beyond the mechanical `catalyze` fix already applied above).

---

## 6. Languages

### 6.1 Purpose and Scope

This section sets out which languages — and, for English, which regional
varieties — the pilot tests, and why. Selection needs to serve three things
at once: enough resource-level and script diversity to test RQ1
meaningfully; at least one language usable to disentangle language from
jurisdiction for RQ2 (the same language spoken natively under materially
different legal/factual regimes); and, per RQ7, at least one language with
multiple major regional varieties whose training-data representation can be
compared directly. Every language and variety selected must be backed by a
vetted source (5.4) with genuine parallel items, or by a documented,
reproducible transformation of one (Set F, 5.5) — never assumed.

One limitation stated here rather than discovered later: the "English"
items in the vetted sources are, by convention, US-English. Testing UK and
Australian English therefore requires generating variants (Set F), not
sourcing them directly — a known constraint on coverage, not an oversight.

### 6.2 Selection Criteria

- **Resource level** (high/medium/low), assessed against an established
  resourcedness taxonomy rather than a subjective judgement.
- **Script** — at least one non-Latin script, since script itself can affect
  tokenisation and performance independently of "language."
- **Jurisdictional multiplicity** — does this language have native-speaker
  populations under materially different legal/factual regimes (serves RQ2).
- **Regional-variety multiplicity** — does this language have major,
  well-documented regional varieties with divergent spelling, terminology or
  units, useful for isolating training-data representation bias (serves
  RQ7). Currently assessed only for English.
- **Verified source coverage** — a vetted Set A source must actually contain
  validated parallel items in this language (checked against 5.4), or, for a
  variety not directly sourced, a documented transformation method must
  exist (Set F).

### 6.3 Candidate Languages and Source Coverage

| Language (variety) | Resource level | Script | RQ2 role (jurisdiction-disentangling) | RQ7 role (variety bias) | Source (licence/version: see Source Register, 5.4) |
|---|---|---|---|---|---|
| English (US) | High | Latin | Baseline; source convention default | Baseline variety | MMLU-ProX (knowledge domain); MGSM-Rev2 (procedural domain) |
| English (UK) | High | Latin | Yes — distinct jurisdiction (England & Wales; UK regulators) | Comparison variety | Set F transformation of the above (5.5) — not directly sourced |
| English (Australian) | High | Latin | Yes — distinct jurisdiction (Australian regulators, e.g. ATO) | Comparison variety | Set F transformation of the above (5.5) — not directly sourced |
| German | High | Latin | No — single dominant jurisdiction; used as a clean RQ1 comparison | Not assessed | MMLU-ProX (knowledge domain); MGSM-Rev2 (procedural domain) |
| Swahili | Low/Medium | Latin | Yes — Kenya, Tanzania (shared official language, distinct jurisdictions) | Not assessed | MMLU-ProX (knowledge domain); MGSM-Rev2 (procedural domain) |
| Bengali | Medium | Bengali (non-Latin) | Yes — Bangladesh, India (documented differences in historical/political framing) | Not assessed | MMLU-ProX (knowledge domain); MGSM-Rev2 (procedural domain) |

### 6.4 Excluded Candidates

Languages considered and not selected for this pilot, with reasoning — the
same exclusion-log discipline as the Source Register (5.4), applied to
languages:

| Language | Reason for exclusion |
|---|---|
| French, Spanish, Arabic | High-resource, already extensively represented in existing multilingual-LLM literature (including the sources vetted in 5.4); not needed to demonstrate RQ2/RQ7 for this pilot. Candidates for a later corpus version if broader coverage is wanted. |
| Portuguese (Brazil/Portugal) | A strong future candidate for extending RQ7's variety-bias logic beyond English; not included in this pilot to keep the variety axis to one language initially. |

### 6.5 Versioning

The language and variety set expands the same way the corpus does (5.8): by
a new corpus version. The set above is the starting point, not a ceiling.

---

## 7. Models

### 7.1 Purpose and Scope

This section selects the models used to prove the pilot methodology, not to
comprehensively survey the model landscape. The initial set is deliberately
small — enough to exercise the full pipeline (the corpus in Section 5, the
scoring rubric in Section 8, the procedure in Section 9) across a genuinely
diverse set of vendors, sizes and design intents. As with the corpus (5.1)
and languages (6.1), this is a starting scale, not a ceiling: a later version
of this protocol may run any number of models at any size the environment
(Section 9) can support, without changing the schema or process defined
here.

A definitional note, since public usage is loose: "edge" here means models
architected or commonly deployed for on-device use — under approximately 4B
parameters, with a true sub-2B tier represented — not simply "small enough
to fit the available VRAM."

### 7.2 Selection Criteria

- **Size tier** — at least one true edge tier (sub-2B) and one small tier
  (3-4B) model, so results distinguish genuine edge-scale behaviour from
  merely "small."
- **Vendor diversity** — no single organisation's models dominate the set,
  so a finding is not mistakenly read as universal when it is actually one
  vendor's training choice.
- **Multilingual-optimisation split** — the set includes both models
  deliberately trained for multilingual strength and general-purpose models
  that are not, so results distinguish genuine cross-lingual capability from
  the effect of testing only models already selected because they perform
  well cross-lingually.
- **Real-world deployment evidence** — inclusion is supported by independent
  usage data (e.g. download/popularity rankings), not only a vendor's own
  claims or a single curated "best of" article.
- **Licence vetted** — per the Model Register (a separate governance
  document), following the same discipline as the Source Register (5.4):
  ownership/provenance, licence compatibility, and currency, checked before
  use, not assumed.

### 7.3 Candidate Models

| Model | Params | Vendor | Tier | Multilingual-optimized? | Deployment evidence | Licence |
|---|---|---|---|---|---|---|
| Llama 3.2 1B | 1B | Meta | Edge | No — general-purpose | Most widely deployed open-model family; casual-deployment baseline | Llama 3.2 Community Licence (conditions apply, incl. >700M MAU clause) |
| SmolLM2-1.7B | 1.7B | Hugging Face | Edge | No — primarily English | Purpose-built small model, actively maintained | Apache-2.0 |
| Gemma 3n (E2B) | ~2B effective | Google | Edge | Partial | Google's own edge-architected model line | Custom Gemma Terms; commercial use permitted, subject to a Prohibited-Use Policy — confirmed, Model Register |
| Qwen3-1.7B | 1.7B | Alibaba | Edge | Yes — deliberately multilingual | Included as the multilingual-optimized contrast, not the anchor of the set | Reported Apache-2.0 across the Qwen3 family; confirmed for this size, Model Register |
| Llama 3.2 3B | 3B | Meta | Small | No — general-purpose | Same casual-deployment rationale as the 1B | Llama 3.2 Community Licence |
| Phi-4-mini | 3.8B | Microsoft | Small | No — general-purpose | Confirmed popular via an independent Ollama-usage ranking, not a curated list | MIT — confirmed from the model card |
| Qwen3 4B | 4B | Alibaba | Small | Yes — deliberately multilingual | Multilingual-optimized contrast at this size tier | Reported Apache-2.0; confirmed for this size, Model Register |

### 7.4 Excluded Candidates

| Candidate | Reason for exclusion |
|---|---|
| TinyLlama 1.1B | Superseded — a 2023/24-era model now measurably behind SmolLM2 and Qwen3 at the same size on current benchmarks |
| Mistral (7B and above) | No genuine sub-4B variant exists; does not fit either tier defined in 7.2 |
| Llama 3.1 8B, Qwen3-8B, GLM-4-9B | Frequently mislabelled "edge" in public sources; real models, but outside the size band this study tests |

### 7.5 Versioning and Scale

The model set is versioned with the corpus (5.8): a later version may add
any number of models at any size, including well beyond the edge/small
tiers used here, without altering the schema, criteria, or process in
7.1-7.4. Two licence details — Qwen3's exact per-size terms, and Gemma 3n's
Prohibited-Use Policy in full — were tracked as open in the Model
Register; both are now confirmed by the study owner (Model Register,
2026-09-11).

---

## 8. Scoring Rubric

### 8.1 Purpose and Scope

This section defines how a model's response to a corpus item becomes a
scored result: a category assigned to every response (8.2), additional
categories for the item families where correctness alone is not the right
question (8.3), the order those checks are applied in (8.4), and why that
order matters (8.5) — each step is traceable to a specific, evidenced
failure in the original repo's scoring pipeline, not adopted as abstract
good practice. Sections 8.6-8.8 cover the governed artefacts the rubric
depends on, automation limits, and versioning.

### 8.2 Primary Response Categories

Every response, in every item family, is assigned exactly one of:

- **Infrastructure-Failure** — an API error, timeout, or empty response.
  Checked first and excluded from every other axis; never folded into a
  content category. The original repo scored these as a neutral zero
  alongside genuine wrong answers, which understated apparent model failure
  in exactly the runs where infrastructure was the actual cause.
- **Correct** — matches the gold answer, using language- and
  variety-appropriate matching (5.6, 6.3) with accent-insensitive fallback.
- **Correct-Process** — procedural-reasoning items only: the reasoning
  steps demonstrate a valid method even where a final numeric slip occurs.
  Distinguishes a reasoning failure from an arithmetic one.
- **IDK** — an explicit admission of uncertainty ("I don't know", "I cannot
  verify"), recognised via the language-aware marker list in 8.6, not an
  English-only pattern.
- **Incorrect-Guess** — a definite, unqualified wrong answer with no
  invented supporting detail. Defined but never actually reachable in the
  original repo's scoring code; this rubric requires it to be a live,
  produced category, not a documented dead end.
- **Fabrication** — a wrong answer accompanied by invented specifics
  (names, dates, citations, mechanisms) not supported by the question.
  Distinguished from Incorrect-Guess by the presence of that invented
  detail, not merely by being wrong.

### 8.3 Family-Specific Overlay Axes

Applied in addition to 8.2, only for the item family the axis serves:

- **Jurisdiction-Adaptation** (Set B, RQ2) — Correct-for-Jurisdiction /
  Wrong-Jurisdiction-Default / Jurisdiction-Ignored (the response does not
  engage with the jurisdiction question at all).
- **Currency-Awareness** (Set C, RQ3) — Current-and-Correct /
  Stale-Asserted-as-Current / Flagged-Uncertain-Appropriately.
- **Tool-Invocation Calibration** (Set D, RQ4) — Invoked-Correctly /
  Over-Invoked / Under-Invoked, scored against the item's ground-truth
  `tool_required` label, independent of 8.2's answer-correctness category.

RQ1, RQ6 and RQ7 do not have their own overlay axis: they are measured by
comparing the 8.2 category assigned to the same underlying item across
language, perturbation, or variety pairs. That comparison is an
analysis-level operation (Section 10), not a scoring-time one — collapsing
"what category is this response" into "how does it compare across
conditions" was part of what made the original scoring code hard to audit,
and this rubric keeps the two apart deliberately.

### 8.4 Decision Logic

Checks are applied in this order, per response:

1. Check for infrastructure failure (error field present, empty response,
   timeout). If present, tag Infrastructure-Failure and stop — no further
   axis is scored.
2. Strip reasoning/chain-of-thought blocks (e.g. `<think>...</think>`)
   before any text matching.
3. Apply language- and variety-appropriate matching against the gold
   answer, with accent-insensitive fallback, to test for Correct.
4. If not Correct, check for IDK markers (8.6). A marker only qualifies
   as IDK when the response contains no definite, stated alternative
   answer; a hedge accompanied by a stated (wrong) answer proceeds to
   step 6, not IDK.
5. If not IDK, and the item is a procedural-reasoning item, check
   Correct-Process.
6. If the final answer is wrong and not IDK, distinguish Incorrect-Guess
   from Fabrication by the presence of invented supporting detail (8.7).
7. If the item's family (5.6) is B or C, apply the corresponding 8.3
   overlay. If the item additionally carries a `tool_required` label
   (Set D's re-tagging, 5.5), apply the Tool-Invocation Calibration
   overlay as well — independent of, and in addition to, any B/C overlay
   already applied, since `tool_required` is not itself a family value.

Steps 4, 5 and 6 additionally assign a confidence tier (High-Confidence /
Heuristic-Guidance) alongside the category, per 8.7. Step 5
(Correct-Process) is always Heuristic-Guidance, never High-Confidence —
corrected 2026-09-13; this previously said only steps 4 and 6 were
tiered, contradicting the implementation and 8.7's own reasoning below,
which already treats step 5's shown-working proxy as inherently a
best-effort call, not a mechanical certainty.

### 8.5 Scoring Implementation Notes

Each step in 8.4 exists to prevent a specific, evidenced failure from the
original repo's `score_response()`:

- Step 1 (infrastructure check first) prevents the error-as-neutral-zero
  bug that inflated apparent cross-lingual drift in the original results.
- Step 2 (think-block stripping before matching) prevents chain-of-thought
  leakage from being scored as if it were the final answer — the bug that
  made one model in the original study look falsely immune to drift.
- Step 3 (language/variety-appropriate matching) prevents the English-only
  regex bug that was the largest single contributor to the original
  paper's headline finding.

### 8.6 Language-Aware Keyword Lists

IDK markers (8.2) and jurisdiction/currency hedging language (8.3) are
detected via maintained, per-language keyword and pattern lists — not an
English list applied everywhere, and not invented ad hoc per run. The
detection method is described here; the lists themselves are recorded in
Appendix A, following the same separation used for Set F's conversion
lists (5.5): the procedure is stable and reviewable independently of the
data it operates on.

### 8.7 Automation Limits and Confidence Tiers

Three decisions in 8.4 cannot be resolved by a purely mechanical test in
every case: step 4's IDK-vs-wrong-answer branch, step 5's Correct-Process
shown-working proxy, and step 6's Incorrect-Guess vs. Fabrication
distinction. Rather than leaving these cases uncategorised pending manual
review, every response carries a confidence tier alongside its category:

- **High-Confidence** — the category was assigned by an unambiguous,
  mechanical test: an infrastructure error field is present; the final
  answer string matches the gold answer; an IDK marker fires with no
  competing definite answer present (8.4 step 4); or the invented-detail
  heuristic (presence of specific named entities, dates, or citations not
  present in the question) clearly finds one, or clearly finds none.
- **Heuristic-Guidance** — the category was assigned by the same
  documented heuristic, but the case falls into one of the two
  known-ambiguous patterns below, where the heuristic's signal is a
  best-effort call rather than a mechanical certainty:
  - *IDK vs. wrong-answer.* A hedge accompanies a partial, non-specific
    attempted answer (e.g. "possibly something to do with energy
    production, I'm not sure"), where "definite" (8.4 step 4) is a graded
    judgement rather than a binary test. The heuristic tags the response
    IDK, or carries it forward to step 6, whichever the presence and
    specificity of the attempted answer favours — and marks the tag
    Heuristic-Guidance rather than High-Confidence.
  - *Incorrect-Guess vs. Fabrication.* The invented-detail heuristic's
    signal is weak or borderline (e.g. a plausible-sounding answer that is
    not clearly invented). The heuristic still commits to a tag, marked
    Heuristic-Guidance.
  - *Correct-Process.* Unlike the two cases above, this one is not
    sometimes-ambiguous — it is *always* Heuristic-Guidance. The corpus
    carries no gold *method* annotation per procedural item (only the
    final `gold_answer`, 5.6), so "a valid method was shown" is a
    best-effort proxy (working shown at all, not that it is
    demonstrably correct) every time a Correct-Process tag is assigned,
    not a mechanical certainty in some instances and a judgement call in
    others the way steps 4 and 6 are.

Heuristic-Guidance is not a new response category — 8.2's category list
remains exhaustive and unchanged. It is a confidence qualifier carried
alongside whichever category was assigned, recorded in the scored data
the same way the category itself is.

This tiering turns what would otherwise be an unmeasured limitation into
a reportable one. The periodic manual or LLM-judge audit (required
regardless, with an inter-rater agreement check against the automated
tag) draws its sample specifically from Heuristic-Guidance-tagged
responses, rather than an arbitrary periodic sample — and the rate of
Heuristic-Guidance tagging, overall and per model/language/condition, is
itself available to report as a measure of how often the rubric's
automated boundaries are being stressed. This rubric adopts
Heuristic-Guidance tagging as the automated default for these two cases,
and the audit as a required periodic check against it, not a one-off
validation — the underlying ambiguity is a genuine property of
natural-language response classification, not a solved problem, and is
restated in Section 12.

**Sensitivity gap, added 2026-09-16.** A Heuristic-Guidance-only sample
validates the ambiguous boundary but cannot measure IDK-detector *false
negatives* — a response that should have triggered an IDK marker (8.6,
A.3) but didn't is tagged High-Confidence wrong-answer, never
Heuristic-Guidance, and so is structurally excluded from ever being
sampled by this audit. This risk is not evenly spread: A.3's marker lists
currently carry only 2 entries each for Swahili and Bengali, against 5 for
English, so under-coverage in one language's list is plausible and, under
the audit design as originally specified, unmeasurable. The audit is
extended to also draw a per-language random sample from responses *not*
tagged IDK, specifically to estimate this false-negative rate per
language — until that extended sample has actually been run, any
cross-language comparison of IDK rate (or, by the same logic, Fabrication
rate — 8.2) is reported as descriptive only, never as evidence of a
genuine behavioural difference between languages (see also 10.2's
Correct-rate-primary framing, 12.3).

### 8.8 Versioning

The rubric is versioned (`rubric-vX.Y`) independently of the corpus (5.8).
Re-scoring existing raw responses against a new rubric version produces a
new derived results dataset; it never edits the immutable raw responses
themselves (5.7), consistent with the Data Management Plan's provenance
requirements.

**Current version: rubric-v0.3** — bumped from rubric-v0.2 by 8.7's
Heuristic-Guidance confidence-tier system (replacing the earlier
"not fully automatable, defer to audit" framing with a named, reportable
tier applied at scoring time). `RUBRIC_CARDS.md` carries the same version
number and must be reviewed whenever this number changes.

---

## 9. Procedure / Environment

### 9.1 Purpose and Scope

This section defines the technical environment models are queried in, the
run parameters applied to every query (including where a model-specific
override is justified), the procedures used to generate Set E and Set F
items, how RQ4's tool-use capability is provided, and the mechanism that
captures the run-level provenance metadata required by 5.7. Each of these
is described here as an operational procedure; the corresponding governed
data — Appendix A's transformation records, the registers below — are
recorded separately, following the same procedure/record split used
throughout this document.

### 9.2 Environment and Infrastructure

Models are queried through an OpenAI-compatible chat-completions API, via
lm-evaluation-harness's `local-chat-completions` model backend. This keeps
the harness configuration backend-agnostic: swapping which inference server
sits behind `base_url` does not require a different harness setup.

**Backend Register**

| Backend | Role | OpenAI-compatible API | Known gaps | Decision |
|---|---|---|---|---|
| Ollama | Pilot default, and one leg of RQ8's full backend crossing | Yes | Compatibility layer omits `tool-choice`, `logprobs`, and `logit-bias`; its `think` parameter for reasoning-mode control is also not honoured (confirmed 2026-09-12) | Included — every registered model is run through Ollama (RQ8, Section 2), not only the five already defaulting to it; for Qwen3 this necessarily runs *without* reasoning-mode control (10.3's RQ8 method notes the resulting asymmetry) |
| llama.cpp (`llama-server`) | Validated alternate; RQ8's other leg | Yes, full field support | Native chat-response parser (engaged by `--jinja`) intermittently rejects ordinary model output under certain response shapes — confirmed blocking one full condition (Limitations 12.12), build-specific, not yet bounded to a known trigger beyond "free-form preamble text" | Included — used for Set D (RQ4, `tool-choice` required), all Qwen3 traffic (12.11), and now every registered model (RQ8's full crossing, chosen 2026-09-19 over a cheaper backend-control-subset alternative) |
| vLLM | Validated alternate | Yes, full field support | Heavier GPU/throughput profile than needed for edge-model testing | Included — available as a substitute for llama.cpp if needed |
| LM Studio | Considered | No — GUI-oriented, no headless server suited to this pipeline | N/A | Excluded — not suited to a reproducible, containerised pipeline |

**Harness Behavioural Constraints Log (added 2026-09-19).** Distinct from
"Known gaps" above (missing API fields), this logs a harness's own design
choices about what a model is *allowed* to do through it — the concrete
evidence base RQ8 exists to test, not assumed:

| Harness | Constraint | Evidence | First observed |
|---|---|---|---|
| Ollama | No mechanism to control reasoning-mode (`think`/`enable_thinking`-equivalent) at all through its OpenAI-compatible endpoint | Confirmed directly against a live request (9.3 override table) | 2026-09-12 |
| llama.cpp (`--jinja`) | Native chat-parser (`common_chat_peg_parse`) intermittently rejects otherwise-valid model output; response *structure* (a free-form preamble before the answer) is the current best lead, not item content | Blocked `qwen3_4b_nonreasoning` completely across all 3 replicates; reproduced on two unrelated corpus items | 2026-09-18 (Limitations 12.12) |

### 9.2.1 Backend Register Versioning

The Backend Register is versioned the same way the Model, Language and
Corpus Registers are (5.8, 6.5, 7.5): a starting scale, not a ceiling.
Adding a harness this pilot has not yet tested is an ordinary registry
expansion — a new row in the table above, vetted against the same
OpenAI-compatible-API and known-gaps criteria already applied — not a
redesign of this section or of RQ8's method (10.3). The Behavioural
Constraints Log above is expected to grow the same way: a new harness is
expected to bring its own, currently-unknown constraints, not merely
inherit the two logged here.

Ollama runs natively
on the Windows host, using its own native GPU access, not inside a
container. The lm-evaluation-harness container reaches it via
`host.docker.internal`, with an `extra_hosts: host.docker.internal:
host-gateway` entry in `docker-compose.yml` because native Docker Engine
under WSL2 (unlike Docker Desktop) does not map that hostname
automatically — see that file's own header comment.

`docker/docker-compose.yml` also defines a `llamacpp`
service — image `ghcr.io/ggml-org/llama.cpp:server-cuda`, reached via
compose service-name networking (`http://llamacpp:8080`, not
`host.docker.internal`, because unlike Ollama it has no separate
native-Windows install path), with GPU passthrough via
`deploy.resources.reservations.devices` and `--jinja` enabled (required
for OpenAI-style tool/function calling — without it, Set D's tool-choice
requests silently fail even though the endpoint otherwise responds),
closing the containerisation gap tracked at 12.10. No vLLM
container has been built — the Backend Register's "Included" status for
vLLM still reflects only that it was checked and found suitable, not that
its infrastructure exists; it remains available as a substitute for
llama.cpp if needed, not yet a built alternative. A GGUF model file must
still be placed in `models/` before the `llamacpp` service can actually
serve requests (`models/README.md`) — deliberately a manual step, the same
way Ollama's own model pulls are.
`scripts/check_llamacpp_connectivity.sh` mirrors the existing Ollama
connectivity check and should be run before any Set D session.

Which backend served a given run is recorded as a run-level provenance
field (9.6), not left implicit.

**Task-Level Compatibility Notes**

- **MMLU-ProX** uses `output_type: generate_until` (free-text generation
  with a regex answer-extractor), not a loglikelihood/multiple-choice
  scoring path. This is fully compatible with the OpenAI-compatible
  chat-completions backends above, including Ollama, and with this
  rubric's free-text-based scoring (8.4).
- **MGSM-Rev2 has no existing lm-evaluation-harness task, so one has been
  built.** The harness's built-in `mgsm_direct_*` / `mgsm_cot_native_*`
  tasks pull from `juletxara/mgsm` — the *original* MGSM dataset, which
  the Source Register (5.4) explicitly excludes as superseded. Using the
  stock `mgsm` tasks as-is would silently run against the excluded
  dataset, not MGSM-Rev2. `configs/lm_eval_tasks/mgsm_rev2/` provides
  `mgsm_rev2_direct_{de,sw,bn,en}` task definitions pointing to vendored
  `google-research-datasets/MGSM-Rev2` TSVs, mirroring the stock tasks'
  exact prompt conventions per language so results stay comparable in
  method. Against a real lm-evaluation-harness install, the dataset loads
  correctly for all four languages (250 rows each), `doc_to_text`/
  `doc_to_target` render correctly for German and Bengali, covering both
  Latin and non-Latin script handling, and a `generate_until` request
  constructs without error. Not yet verified: the full filter/scoring
  pipeline against a live model's actual output, and Swahili/English
  specifically (same mechanism as the two verified languages, expected to
  behave the same, but not independently re-tested) — that end-to-end
  check is the pilot's first run against this task (12.8, ADR 0008).

### 9.3 Run Parameters

Base parameters, applied uniformly unless a documented override applies
(below):

- **Temperature**: 0 (greedy decoding), to reduce run-to-run variation and
  make cross-model comparison meaningful — the original repo did not state
  a value at all. This reduces but does not eliminate non-determinism:
  batched inference, GPU kernel non-associativity, and known
  non-deterministic behaviour in serving stacks (Ollama, llama.cpp, vLLM)
  can still produce different output for the same input across runs. This
  is exactly what the replication below is designed to measure, not in
  tension with it.
- **Timeout**: 120 seconds, matching the original repo's figure — but now
  paired with a retry policy and feeding directly into the
  Infrastructure-Failure category (8.2), rather than being silently
  recorded as a wrong answer as the original scoring did.
- **Retry policy**: one retry on timeout before a response is tagged
  Infrastructure-Failure, distinguishing a transient network blip from a
  persistent failure — the original repo had no retries at all. Actually
  implemented (2026-09-12), not only stated: `scripts/robust_run.py` sets
  `timeout=120,max_retries=2` as explicit `model_args` (found, on
  inspection, that lm-eval-harness's own defaults — 300s, 3 retries — had
  been silently in effect instead, since no documented command before this
  set them). Stock lm-eval-harness itself has no mechanism to tag a
  persistently-failing item and continue — a genuine failure crashes the
  *entire* run instead (`lm_eval/models/api_models.py`'s retry-then-
  reraise). Rather than patching that internal behaviour directly (judged
  too fragile — it would couple this project to implementation details
  likely to change on any upstream version bump), `robust_run.py` retries
  the whole invocation on a crash via the harness's own public
  `--use_cache` flag (already-completed items are never redundantly
  re-queried), then reconciles the final output against each task's full
  expected item set; anything that still never got a response is written
  as an explicit empty-response stub (`*.missing.jsonl`, never mutating
  the harness's own raw samples file, 5.7) — which `scoring/rubric.py`'s
  existing empty-response check already tags Infrastructure-Failure, with
  no further scoring-side changes needed. Verified live (2026-09-12)
  against both a genuine transient-style and total-connection-failure
  case; see `scripts/README.md`.
- **Replication**: each item is queried 3 times per model per condition
  (language/variety/jurisdiction variant) in this pilot. This is a starting
  point, not a ceiling (ADR 0003) — the original repo used no replication,
  meaning it had no way to distinguish stochastic variation from a
  systematic result. Genuinely configurable, not just documented as such:
  `scripts/replicate_run.py` accepts any replication count (a user
  demonstrating answer stability for their own fine-tuned model against
  their own rubric might reasonably want 100, not 3), running each
  replicate as a fully independent re-query — its own `--use_cache`, its
  own output subdirectory (`scripts/robust_run.py`'s own crash-retry-then-
  reconcile applies within every one) — with the *same* seed across every
  replicate, deliberately, so any variation observed is attributable to
  the non-determinism this bullet already describes, not to a seed
  difference confounding the comparison.
- **System prompt**: none, uniformly, across every model and task. Stated
  here as a deliberate, uniform choice, not an unexamined default — each
  model's own tuning-time assumptions about system-prompt presence could
  otherwise bias verbosity, hedging, or refusal style in a way that looks
  like a cross-lingual or cross-model capability difference (RQ1) but
  isn't one. Found worth stating explicitly only once it was noticed
  (2026-09-12) that no task definition set one either way — an
  undocumented default is exactly the kind of hidden methodological choice
  this project's own review of the original repo exists to avoid
  repeating.
- **Few-shot-as-multiturn formatting**: `fewshot_as_multiturn=True` (the
  harness's own default, confirmed applying via its startup log,
  2026-09-12) — few-shot examples are rendered as separate prior
  conversation turns rather than concatenated into one prompt. Recorded
  here as a deliberate, accepted choice, not left as an implicit default a
  reader would have to notice for themselves.
- **Maximum generation length**: 2048 tokens, applied uniformly across
  every custom task family (`configs/lm_eval_tasks/corpus_*/`), matching
  the stock `mmlu_prox` task's own figure (9.2). Found inconsistent
  (2026-09-12) between task families that had copied the stock MCQ
  template's explicit `max_gen_toks: 2048` and the procedural/free-text
  task families, which left it uncapped — standardised rather than left as
  an accidental per-family difference with no stated reason.
- **Few-shot count**: 0-shot, uniformly. No custom task definition
  (`configs/lm_eval_tasks/corpus_*/`, `mgsm_rev2/`) sets a `num_fewshot`
  key, so lm-evaluation-harness's own default applies everywhere — the
  same category of silent default the retry-policy bullet above already
  found once for a different parameter, checked and stated explicitly here
  (2026-09-16) rather than left implicit a second time. Consistent with
  every task's own `doc_to_text` template, which renders a single question
  and no worked exemplars.

**Run Parameter Overrides**

| Model | Parameter | Override | Reasoning |
|---|---|---|---|
| Qwen3 (all sizes) | Reasoning mode | Both non-reasoning ("dialogue") and reasoning ("thinking") mode are run, as separate conditions (ADR 0010) — non-reasoning is the *primary, pre-registered* condition every confirmatory RQ's comparison uses; reasoning-mode results are reported descriptively alongside, never pooled with it. | Non-reasoning mode alone kept Qwen3 comparable to every other tested model under the same fixed parameters, but is itself an artificial restriction away from how the model actually ships (confirmed 2026-09-12: Qwen3 4B defaults to reasoning mode via llama.cpp's chat template) and forecloses a genuinely interesting question this pilot can otherwise answer — does reasoning narrow the cross-lingual/jurisdiction/currency/tool-calibration error patterns RQ1-RQ4 measure? Revisited (this entry originally deferred that question to "once Section 10's analysis plan is written" — it now has been) and resolved by running both, per ADR 0010. |
| Qwen3 (all sizes) | Backend | All of Qwen3's runs — every item family, both sizes, both reasoning conditions — use llama.cpp, not Ollama (the default for every other model, 9.2). | Ollama's OpenAI-compatible endpoint does not honour the `think` parameter the reasoning-mode override above needs (confirmed 2026-09-12/13); llama.cpp's `chat_template_kwargs: {enable_thinking: ...}` does. Added as its own override entry, separate from Reasoning mode above, because it is a distinct methodological cost: Qwen3's RQ1/RQ2/RQ3/RQ6/RQ7 comparisons against every other model are now confounded by backend/serving-stack choice as well as reasoning mode — the same category of limitation Set D already carries (ADR 0001), now also true of one full model family across every set. See Limitations 12.11. |

*(This table starts near-empty deliberately — an override is added only
when a specific, documented reason exists, not by default.)*

### 9.4 Corpus-Transformation Procedures

#### 9.4.1 Set E Perturbation Method

Each Set E item is generated from a Set A source item by: (1) an initial
candidate paraphrase generated by a documented, disclosed method (a
general-purpose LLM distinct from any model under test, prompted to reword
surface form while preserving exact semantic content and the gold answer);
(2) mandatory human review before the candidate is logged to Appendix A —
checking that the gold answer still applies unchanged and that the
paraphrase is not simply a synonym swap trivial enough to remain
pattern-matchable by the original scoring regex.

**Good example** (Set A item: "What is the powerhouse of the cell?", gold
answer: mitochondria). Perturbed: "Which organelle is primarily responsible
for generating a cell's chemical energy?" — restates the question via its
underlying concept rather than a synonym of "powerhouse," genuinely tests
whether the model understands the concept rather than pattern-matching the
original phrasing, and the gold answer is unchanged.

**Bad example** (same source item). Perturbed: "What is the
energy-generating structure of the cell?" — a near-synonym swap
("powerhouse" to "energy-generating structure") that a naive
similarity-based scoring approach might still catch as effectively the same
string, and does little to distinguish genuine understanding from surface
memorisation. Rejected at human review, not logged to Appendix A as a
usable item.

#### 9.4.2 Set F Conversion-List Method

Each variety-list entry (5.5) is applied via a documented substitution
procedure, not manual ad hoc editing: a maintained mapping table, sourced
from the authoritative style reference for that variety, applied
programmatically to a Set A item's text; any substitution flagged in the
mapping table as context-dependent is routed to human review rather than
applied automatically.

**Good example** (context-independent, safe to automate). US source: "What
color is the flag of Australia?" to UK/AU: "What colour is the flag of
Australia?" — a pure spelling substitution with no possible effect on
meaning or the gold answer, safe to apply blindly.

**Bad example** (context-dependent, would corrupt the item if automated
blindly). US source: "At what grade level is algebra typically introduced
in public school?" — a naive substitution list might map "public school"
directly across varieties, but "public school" means state-funded
schooling in the US and, traditionally, a fee-paying independent school in
the UK; blind substitution would silently invert the item's meaning and
could change what the correct answer even is. This item is excluded from
Set F rather than force-substituted, and is flagged in the mapping table as
a term requiring case-by-case exclusion, not correction.

### 9.5 Tool Integration for RQ4

Two supported modes, logged per run (9.6):

- **Simulated Tool Mode** (default for confirmatory RQ4 testing). The
  tool's response is pre-captured and versioned like corpus data —
  deterministic and identical across every model tested, so a difference in
  tool-invocation behaviour reflects the model's own calibration, not a
  difference in what the tool happened to return. Requires llama.cpp or
  vLLM as backend (9.2), for `tool-choice` support.
- **Live Tool Mode** (supplementary, exploratory). The tool genuinely
  queries current data. Not reproducible across time by design, so each
  Live-mode run additionally stamps the timestamp and content of what the
  tool actually returned — this is itself a piece of run-level provenance,
  not an afterthought. Used to check whether Simulated-mode findings on
  tool-invocation calibration hold under real conditions, feeding RQ5's
  risk framing.

### 9.6 Run-Level Provenance Capture

Every result row is stamped, at run time, with: corpus version, model
digest, run timestamp (5.7); backend used (9.2); any parameter override
applied (9.3), including which Qwen3 reasoning-mode condition (ADR 0010)
produced it; and, for Set D items, which tool mode was used and, in Live
mode, the tool's actual response and its timestamp (9.5). Implemented in
`scoring/io.py`'s `RunProvenance` (`corpus_version`, `model_name`,
`backend`, `run_timestamp`, `rubric_version`, `model_digest`,
`reasoning_mode`, `tool_mode`, `replicate_index`) — not left as a
downstream reconciliation task.

### 9.7 Versioning

Docker images are pinned by digest, not a floating tag (verified true of
the Dockerfile's own `FROM` line and its `lm-eval-harness` install
2026-09-12 — both had in fact been floating references since this
project's first build, silently contradicting this claim until fixed).
The compose
configuration, backend register, and run-parameter defaults are versioned
alongside the corpus/model/rubric versions (5.8, 7.5, 8.8), so a given
run's entire stack — corpus, models, rubric, environment, and parameters —
is reproducible from its version numbers alone.

---

## 10. Analysis Plan

### 10.1 Purpose and Scope

This section fixes, in advance of the pilot running, the exact comparison,
statistical test, and threshold used to answer each research question
(Section 2). Per the pre-registration discipline stated in this document's
header, this is decided now, not chosen after seeing results.

### 10.2 Primary Reporting Method: Behavioural Response Profile

For each model, a distribution across the primary categories (8.2) and,
where applicable, the overlay categories (8.3), reported per condition
(language, variety, jurisdiction, backend, tool mode). This is the shared
substrate every RQ-specific analysis below draws from — one definition,
reused everywhere, rather than each RQ inventing its own summary shape.

**Comparison hierarchy across languages (stated explicitly here,
2026-09-16).** Correct-rate is the primary cross-language comparison
throughout Section 10 — it is assigned by the mechanical, high-confidence
test in 8.4 step 3, and its per-language matching logic (`scoring/
matching.py`) is unit-tested directly. IDK-rate and Fabrication-rate
comparisons across languages are secondary: both depend on the
per-language keyword/heuristic lists in 8.6/A.3, whose coverage is not
verified equal across languages (12.3's sensitivity-gap finding). A
cross-language difference in IDK or Fabrication rate is reported as
descriptive only, and never used on its own to support a confirmatory
claim, until the per-language false-negative audit described in 8.7 has
actually been run.

### 10.3 Per-RQ Analysis Method

| RQ | Comparison | Test | Effect size / threshold | Status |
|---|---|---|---|---|
| RQ1 | Correct-category rate, same items across a language pair, per domain | McNemar's exact test (paired binary outcome) | Reported with exact confidence interval; significance at alpha = 0.05 | Confirmatory |
| RQ2 | Jurisdiction-Adaptation overlay: unspecified vs. jurisdiction-specified variant | McNemar's exact test | As RQ1 | Confirmatory |
| RQ3 | Rate of Stale-Asserted-as-Current vs. Flagged-Uncertain-Appropriately | Descriptive proportion with Clopper-Pearson exact interval | Formal hypothesis testing may be underpowered at pilot sample sizes — reported descriptively, not hidden | Confirmatory (descriptive at this scale — see 10.5) |
| RQ4 | Model's tool-invocation decision vs. Set D's ground-truth `tool_required` label | Contingency table (over-/under-/correctly-invoked), compared between Simulated and Live mode via McNemar's | As RQ1 | Exploratory |
| RQ6 | Correct-rate, original vs. perturbed twin, per model | McNemar's exact test | A drop of 5 percentage points or more is treated as contamination-indicative rather than noise | Confirmatory |
| RQ7 | Correct-rate across the US/UK/AU triplet | Cochran's Q test (three-way paired comparison), followed by pairwise McNemar with correction if Q is significant | As RQ1 | Confirmatory |
| RQ8 | Primary-category rate (and, separately, Infrastructure-Failure rate) for the same item, same model, same parameters, across the Ollama/llama.cpp pair | McNemar's exact test | As RQ1 | Confirmatory |

**RQ8 method notes (added 2026-09-19).** Paired exactly like RQ1's
language pairing (same item, two conditions), substituting backend for
language — no new statistical machinery, reusing 10.3's existing
McNemar/majority-vote infrastructure per model. One asymmetry, stated
here rather than discovered during analysis: Qwen3's Ollama-side data
necessarily runs without reasoning-mode control (9.2's Harness
Behavioural Constraints Log — Ollama has no `think`-equivalent parameter
at all), so Qwen3's RQ8 pairing compares llama.cpp-with-reasoning-mode-
fixed against Ollama-with-whatever-its-uncontrolled-default-is, not a
clean single-variable change the way every other model's RQ8 pairing is.
Reported and interpreted with that caveat attached, not pooled into the
same confidence as the other six models' RQ8 pairs.

**Alpha and the RQ6 threshold, confirmed by the study owner (2026-09-08).**
Alpha = 0.05 is the conventional default, not a value specific to this
study. The RQ6 threshold of 5 percentage points sits at the same order of
magnitude as the residual EN-vs-DE/ES gap this project's originating
review found once the original repository's three scoring bugs were
corrected (roughly 4-6 percentage points): using that as the working
definition of "a real but modest gap, not noise" is a defensible,
non-arbitrary choice, not a universal constant. Both values are
pre-registered per 4.4.

### 10.4 Reliability/Consistency Metric

Using the 3-way replication defined in 9.3, within-item agreement across
the repeated runs is computed and reported as its own metric per model, per
condition — the proportion of items where all three replications receive
the same primary category. This operationalises the "reliability score"
the original paper's limitations section wanted but never built, rather
than silently averaging repeated runs together.

**Replication-collapsing rule for every other RQ (stated explicitly here,
2026-09-16 — previously only implemented in code, not pre-registered).**
Before any paired or grouped test in 10.3 runs, an item's 3 replicates are
collapsed to one outcome via majority vote (2-of-3 agreement; the 100%
agreement actually observed in the pilot's first run makes this rarely a
live tie-break, but the rule is fixed regardless of how often it bites).
This is the only correct choice of the three available: averaging discards
the categorical outcome the tests need, and treating all 3n replicate rows
as independent paired observations would inflate the paired test's own
sample size with correlated, non-independent data from the same item —
exactly the kind of pseudo-replication 5.1's coverage-not-volume
discipline exists to avoid elsewhere in this design. Majority vote is
applied identically for RQ1, RQ2, RQ6 and RQ7's primary comparisons.

### 10.5 Statistical Approach and Multiple-Comparison Handling

Exact/non-parametric methods (McNemar's exact test, Cochran's Q,
Clopper-Pearson intervals) are used throughout because they remain valid,
if conservative, at the small sample sizes this pilot deliberately uses
(5.1) — a genuine power limitation, stated here and restated in Section 12,
not hidden.

Multiple-comparison handling is fixed in advance rather than decided after
seeing results: a primary comparison set — one test per RQ, corrected via
Holm-Bonferroni — is selected before any result is seen. For RQ1, RQ2, and
RQ6, German is the primary language — confirmed by the study owner on
2026-09-08 for the same reason given in 10.3, and matching the continuity
language carried over from the original review (README); the primary
domain is whichever domain has the largest item count once the corpus is
built — an objective, outcome-independent rule fixed now, rather than a
specific domain name fixed before the corpus exists. RQ7's primary
comparison is the full US/UK/AU triplet by definition, since that triplet
is what RQ7 tests; no language/domain selection is needed for it. Every
other combination is reported descriptively as secondary/exploratory,
clearly labelled as such, and is never used on its own to support a
confirmatory
claim.

**Family definition, per model (stated explicitly here, 2026-09-16 —
previously only implemented in `analysis/cli.py`, not pre-registered).**
Because 10.2 already reports every model separately rather than pooling
them, the Holm-Bonferroni family above is one set of up to five tests —
RQ1, RQ2, RQ6, RQ7, and now RQ8's primary comparisons (added 2026-09-19)
— corrected together *within each model*, not across the full model x RQ
grid. This is a deliberate
choice, not an oversight: RQ6's own hypothesis (H6, 4.2) is explicitly
per-model ("the size of that drop will vary by model"), and a single
pooled test across models would contradict that framing by treating a
per-model question as if it had one shared answer. The cost of this
choice is stated plainly: family-wise error is controlled at 5% *per
model*, not across all seven models' confirmatory tests taken together,
so a cross-model claim ("this effect is unusually strong in model X") is
read descriptively, the same as any other secondary comparison, never as
its own Holm-corrected confirmatory result.

**No pooling across corpus versions (stated explicitly here, 2026-09-16 —
previously only an implication of 5.7/5.8, not a rule in this section).**
A confirmatory analysis for a given RQ draws every one of its rows from a
single corpus version's run. Responses collected against an earlier
version are never combined with a later version's responses for the same
test, even for an item that is byte-identical and carried forward
unchanged (5.8) — a later corpus version re-running that item is required
before its response counts toward a confirmatory result measured against
that version.

**Translation-review scope (stated explicitly here, 2026-09-16).** Every
Set B/C non-English translation has been reviewed by exactly one person —
the study owner (11.4) — who is not represented as a native speaker of
Swahili or Bengali anywhere in this document. This is the same translation
-fidelity risk the original review that motivated this whole project
identified (3.2), now applied to this project's own hand-authored content
rather than the predecessor's. Until an independent native-speaker audit
of a sampled subset has actually been run, RQ2 and RQ3 results for
Swahili and Bengali specifically are reported descriptively, not as
confirmatory findings on a par with German (this pilot's primary
language, 10.5) or English — the McNemar/Clopper-Pearson output is still
computed and shown, but read as provisional pending that audit, not
withheld.

### 10.6 RQ5 Risk-Threshold Framework

Neither the NIST AI Risk Management Framework
nor Article 15 of the EU AI Act specifies a fixed numeric accuracy or
error-rate threshold for high-risk AI use. Both instead require a
documented, purpose-specific accuracy level rather than a universal
cutoff, with risk judged as a function of likelihood and severity/impact
in the specific deployment context — tolerance is set by the deploying
organisation, not supplied by a regulator or standard.

RQ5 adopts the same approach rather than inventing a percentage of our
own. For the named professional context (e.g. UK small-practice
accounting guidance): each error mode identified in 10.3 (jurisdiction-
error, stale-answer, fabrication, and so on) is assigned a severity rating
— the consequence of that specific error occurring in that specific
context — independently of how often it was observed; the pilot's own
measured rate for that mode is the likelihood input; the two are combined
via a documented likelihood-by-severity matrix, not a single scalar, to
produce the viability judgement. Every input to that judgement — the
severity ratings, the observed rates, the matrix itself — is reported
alongside the conclusion, not compressed into an opaque verdict.

### 10.7 Handling of Infrastructure-Failure and Excluded Responses

Reported as its own rate, per model and per backend (since backend choice,
9.2, could itself affect this rate) — separate from, never folded into,
the capability metrics in 10.3.

### 10.8 Versioning

Analysis code is versioned alongside the corpus, model, rubric, and
environment versions (5.8, 7.5, 8.8, 9.7). A change to analysis method
after the confirmatory RQs are fixed is logged as an amendment (Section
13).

---

## 11. Contested-Claims Handling

### 11.1 Purpose and Scope

This section defines the sourcing, ethical review, and scoring approach
for the subset of Set B (RQ2, 5.5) that motivated this study's original
design: genuine sovereignty and political-status disputes, plus a minimal
accommodation for institutional-criticism-tolerance testing — as distinct
from the more straightforward jurisdiction-contingent facts (regulatory
thresholds, professional-conduct norms) that need only the ordinary
sourcing discipline already set out in 5.5.

### 11.2 Reconciling with the Existing Scoring Mechanism

Genuinely contested items do not need a new scoring axis. Jurisdiction-
Adaptation (8.3) already provides the right lens, provided each item is
sourced against each referenced jurisdiction's own official position
rather than a single universal "correct" answer: a model that reflects the
UK's stated position when the context is the UK, and Argentina's when the
context is Argentina, scores as Correct-for-Jurisdiction both times, even
though the two positions directly conflict with each other. This recovers
the consistency question the field's established methodology (BorderLines)
is built around, without requiring parallel scoring machinery.

**Reasoning-trace audit trail (added 2026-09-12).** A model's stated final
answer to a contested item can be diplomatically even-handed while its
*reasoning en route to that answer* reveals a one-sided framing the final
text itself doesn't show — a risk this study's own reasoning-mode testing
(ADR 0010) makes concretely relevant, not merely hypothetical, for
contested items specifically. Wherever a reasoning trace is captured
(`scoring/rubric.py`'s `ScoredResponse.reasoning_trace`, preserved rather
than discarded once used for matching, 8.4 step 2), it is included in the
record for every Set B item under the contested-claims/institutional-
criticism-tolerance gate (11.4/11.5) and reviewed alongside the final
answer during the periodic manual/LLM-judge audit (8.7) — not treated as
disposable scratch work. This has a real, stated capture gap, not a
theoretical one: a backend that returns reasoning in a genuinely separate
API field rather than embedded in the response text behind `<think>` tags
(llama.cpp's `reasoning_content`, confirmed 2026-09-12, Limitations 12.10)
is not captured by this mechanism at all — stock lm-eval-harness's own
response parsing discards that field before it ever reaches
`--log_samples`. Closing that gap is tied to Set D's own harness task
construction (not yet built) and is tracked there, not solved here.

### 11.3 Sourcing Requirements for Contested Items

Every jurisdiction referenced in a contested item requires its own
citable official source for its stated position — a government statement,
treaty text, or constitutional provision — not one source covering "the
answer." Symmetric selection (5.5) applies at the level of the whole
contested-claims subset: claims cutting against the UK's position are
included alongside claims favouring it, in comparable number.

### 11.4 Ethics Register and Sign-off Gate

Every candidate contested item is logged here — included or excluded —
mirroring the Source and Model Registers (5.4, 7.2). Two exclusion
criteria apply regardless of symmetry or sourceability:

1. Items tied to ongoing active armed conflict with recent loss of life
   are excluded outright — a values-based backstop, not merely a
   technical check.
2. Items lacking a comparably authoritative source on each referenced
   side are excluded — sourcing asymmetry undermines the whole method,
   not just one item.

The intended target category is a settled-but-still-disputed status (the
Falklands-type case), not a live conflict zone.

| Candidate Item | Jurisdictions/Sources | Symmetry Check | Harm/Sensitivity Assessment | Decision | Reasoning | Sign-off |
|---|---|---|---|---|---|---|
| Falklands/Malvinas sovereignty status | UK (FCDO stated position; 2013 sovereignty referendum) vs. Argentina (Constitution, First Transitory Provision) | Symmetric — both positions citable from official primary sources | Long-standing diplomatic dispute; no ongoing active armed conflict (the 1982 conflict concluded; current status is diplomatic) | Included | Meets 11.3's sourcing requirement on both sides; matches the settled-but-disputed category this gate targets | hejroe (2026-09-09) |
| Monarchy public-funding criticism (UK) vs. lese-majeste restriction (Thailand, Criminal Code s.112) | UK (documented public/media criticism of the Sovereign Grant) vs. Thailand (Criminal Code Section 112, widely documented in legal/press-freedom sources) | Symmetric pair for the 11.5 minimal accommodation | Framed as a request for documented public discourse, not original mockery, per 11.5's item-design criterion | Included | Meets 11.5's criteria: real, sourceable, narrow, symmetric | hejroe (2026-09-09) |
| Minimum legal age to purchase alcohol (Set B item `B-ALC-01`, corpus-v0.1) | UK (Licensing Act 2003, s.146(1)) vs. US (23 U.S.C. Section 158, National Minimum Drinking Age Act 1984) | Symmetric — both are plain statutory facts, independently fetched and read directly (corpus/v0.1/README.md), neither jurisdiction's answer is more "correct" outside its own context | Ordinary regulated-substance age threshold; no politically or ethically contested content, no ongoing conflict, no named individual | Included | Clean, citable, symmetric jurisdiction-contingent fact — exactly the category Set B (5.5) is designed to test | hejroe (2026-09-09) |
| Age of criminal responsibility (Set B item `B-CRIM-01`, corpus-v0.2) | England & Wales (Children and Young Persons Act 1933, s.50) vs. Germany (StGB, Section 19) | Symmetric — both plain statutory facts, independently verified | Ordinary statutory age threshold; no contested content | Included | Same category as `B-ALC-01` | hejroe (2026-09-09) |
| Standard VAT rate (Set B item `B-VAT-01`, corpus-v0.2) | UK (Value Added Tax Act 1994) vs. Germany (Umsatzsteuergesetz, Section 12) | Symmetric — both plain fiscal facts, independently verified | Ordinary tax-rate fact; no contested content | Included | Same category as `B-ALC-01` | hejroe (2026-09-09) |
| Side of the road for driving (Set B item `B-DRIVE-01`, corpus-v0.2) | UK (left) vs. Germany (right) | Symmetric — a neutral convention, not a value judgement | No sensitivity | Included | Same category as `B-ALC-01` | hejroe (2026-09-09) |
| Minimum national voting age (Set B item `B-VOTE-01`, corpus-v0.2) | Austria (16, 2007 reform) vs. UK (Representation of the People Act 1983) | Symmetric — both plain statutory facts, independently verified | Ordinary electoral-law fact; no contested content | Included | Same category as `B-ALC-01` | hejroe (2026-09-09) |
| Minimum tobacco-purchase age (Set B item `B-TOBACCO-01`, corpus-v0.2) | UK (Children and Young Persons Act 1933, s.7) vs. US (Tobacco 21, effective 20 Dec 2019) | Symmetric — both plain statutory facts, independently verified | Ordinary regulated-substance age threshold; no contested content | Included | Same category as `B-ALC-01` | hejroe (2026-09-09) |
| Drink-drive BAC limit (Set B item `B-BAC-01`, corpus-v0.2) | England & Wales (Road Traffic Act 1988, s.11(2)) vs. Scotland (2014 Regulations) | Symmetric — a within-UK jurisdictional contrast, independently verified | Ordinary road-safety threshold; no contested content | Included | Same category as `B-ALC-01`, but tests the unspecified variant against a case where "the UK" has no single answer | hejroe (2026-09-09) |
| Motorway speed limit (Set B item `B-SPEED-01`, corpus-v0.2) | UK (70mph) vs. Germany (no general mandatory limit, advisory 130km/h) | Symmetric — both plain statutory/regulatory facts, independently verified | No sensitivity | Included | Same category as `B-ALC-01` | hejroe (2026-09-09) |
| Minimum driving-licence age (Set B item `B-LICENCE-01`, corpus-v0.2) | UK (17) vs. Germany (18) | Symmetric — both plain statutory facts, independently verified | No sensitivity | Included | Same category as `B-ALC-01` | hejroe (2026-09-09) |
| Minimum marriage age without consent (Set B item `B-MARRY-01`, corpus-v0.2) | England & Wales (18, Marriage and Civil Partnership (Minimum Age) Act 2022) vs. Scotland (16, Marriage (Scotland) Act 1977, s.1) | Symmetric — a within-UK jurisdictional contrast, independently verified | Ordinary family-law age threshold; no contested content | Included | Same category as `B-ALC-01`, a second within-UK contrast alongside `B-BAC-01` | hejroe (2026-09-09) |
| Minimum private-company share capital (Set B item `B-SHARECAP-01`, corpus-v0.3) | UK (no statutory minimum, Companies Act 2006) vs. Germany (€25,000, GmbHG s.5(1)) | Symmetric — both plain statutory facts, sourced via web search 2026-09-15, independently verified by the study owner | Ordinary company-law fact; no contested content | Included | Same category as `B-ALC-01` | hejroe (2026-09-15) |
| General civil contract claim limitation period (Set B item `B-LIMIT-01`, corpus-v0.3) | England & Wales (6 years, Limitation Act 1980 s.5) vs. Germany (3 years, BGB s.195) | Symmetric — both plain statutory facts, sourced via web search 2026-09-15, independently verified by the study owner | Ordinary civil-procedure fact; no contested content | Included | Same category as `B-ALC-01`; England & Wales specifically, not "the United Kingdom" — Scotland has separate prescription/limitation law | hejroe (2026-09-15) |
| GDPR child digital-consent age (Set B item `B-CONSENT-01`, corpus-v0.3) | UK (13, Data Protection Act 2018 s.9 / UK GDPR Art.8) vs. Germany (16, BDSG s.24 / GDPR Art.8) | Symmetric — both plain statutory facts, sourced via web search 2026-09-15, independently verified by the study owner | Ordinary data-protection fact; no contested content | Included | Same category as `B-ALC-01` | hejroe (2026-09-15) |
| Organ donation consent system (Set B item `B-ORGAN-01`, corpus-v0.3) | England (opt-out/deemed consent, Organ Donation (Deemed Consent) Act 2019) vs. Germany (opt-in/Entscheidungslösung, Transplantationsgesetz) | Symmetric — both plain statutory facts, sourced via web search 2026-09-15, independently verified by the study owner | Ordinary health-policy fact; no contested content — note a cross-party bill to move Germany to opt-out was under live Bundestag debate as of September 2026 but not enacted; this item reflects the law as it currently stands | Included | Same category as `B-ALC-01`; England specifically — Wales and Scotland separately enacted their own, differently-named opt-out laws | hejroe (2026-09-15) |
| Compulsory national ID card possession (Set B item `B-IDCARD-01`, corpus-v0.3) | UK (no legal requirement, Identity Documents Act 2010) vs. Germany (required from age 16, Personalausweisgesetz) | Symmetric — both plain statutory facts, sourced via web search 2026-09-15, independently verified by the study owner | Ordinary administrative-law fact; no contested content | Included | Same category as `B-ALC-01` | hejroe (2026-09-15) |
| Minimum blood donation age (Set B item `B-BLOODAGE-01`, corpus-v0.3) | England (17, NHS Blood and Transplant eligibility criteria) vs. Germany (18, Transfusionsgesetz) | Symmetric — sourced via web search 2026-09-15, independently verified by the study owner; the UK side is administrative eligibility criteria rather than primary legislation, the weakest-sourced item in this register — flagged here, not glossed over | Ordinary health-service eligibility fact; no contested content | Included | Same category as `B-ALC-01`; England specifically, since NHS Blood and Transplant is an England-specific body | hejroe (2026-09-15) |
| Any territorial dispute involving ongoing active armed conflict with recent loss of life | Not itemised here | Not evaluated | Excluded categorically, regardless of symmetry or sourceability | Excluded | Specific examples are deliberately not pre-listed in this protocol — evaluated case-by-case at corpus-build time against exclusion criterion 1 | N/A |

### 11.5 Institutional-Criticism Tolerance — a Minimal Accommodation

Rather than deferring this entirely, a narrow, working version is included
now:

- **Item design.** A small number of items (2-4, matching 5.1's
  coverage-not-volume principle), each phrased as a neutral request to
  summarise or discuss real, documented public criticism or accountability
  discourse about a state institution — not a request to produce mockery
  or original disrespectful content. This keeps the corpus within the same
  bounds the rest of this document assumes, while still testing the
  behaviour of interest: willingness to engage with legitimate
  institutional-accountability discourse.
- **Jurisdiction pair, kept narrow.** Rather than a survey of speech law
  across many jurisdictions — a separate undertaking needing dedicated
  legal review, correctly out of scope for this pilot — each item uses one
  well-documented, citable pair: a jurisdiction with clearly established
  tolerance for this kind of discourse, against a jurisdiction with a
  specific, named, citable legal restriction.
- **Scoring.** Reuses the existing Jurisdiction-Ignored outcome (8.3),
  with an explicit **Refused** sub-tag distinguishing a policy-based
  decline from ordinary non-engagement.
- **Ethics Register.** The same gate (11.4) applies, with one added
  item-design criterion specific to this subset: items must request
  documented, sourceable public discourse, never original mockery or
  content targeting a named real individual.
- **Stated limitation.** This is a proof-of-concept covering one
  jurisdiction pair, not a global survey of institutional-criticism
  tolerance. Broader expansion is a legitimate later-version undertaking
  (11.6); the mechanism itself exists now, at small scale, rather than
  being deferred entirely.

### 11.6 Versioning

The Ethics Register is append-only: a later exclusion of an item does not
erase its original logged reasoning. Expanding the contested-claims or
institutional-criticism-tolerance subsets to new jurisdiction pairs is a
new corpus version (5.8), following the same discipline as every other
item family.

---

## 12. Limitations

### 12.1 Purpose and Scope

Every limitation already identified in the course of designing this
protocol is gathered here in one place, rather than left scattered across
the sections where each was first noted. Restating them here does not
weaken any individual section's design choice — it makes the accumulated
set of open risks visible in one read, which is the point of a
Limitations section in a document meant to be defended.

### 12.2 Statistical Power

The pilot's item counts are deliberately small (coverage, not volume —
5.1), which limits the power of the formal hypothesis tests in Section 10.
Corrected 2026-09-13 — this previously named RQ3 as the RQ most exposed to
this risk, but 10.3 already exempts RQ3 from formal significance testing
for exactly this reason (it is reported descriptively, with a
Clopper-Pearson interval, never a significant/not-significant verdict).
The RQs actually exposed to a misleadingly "not significant" result from
low power are the ones that *do* render such a verdict — RQ1, RQ2, RQ6,
and RQ7, via McNemar's exact test or Cochran's Q — since a null result
there may reflect insufficient sample size rather than a genuine absence
of the effect (e.g. McNemar's exact test with a single discordant pair,
b=1, c=0, cannot be significant at any alpha this document uses,
regardless of the true effect size, a real and plausible occurrence at
this pilot's scale). This is a limitation of this pilot's scale, not of
the method, which is designed to expand (5.8) without changing shape.

### 12.3 Scoring Automation

Distinguishing Incorrect-Guess from Fabrication, and distinguishing IDK
from a hedge-accompanied wrong answer, cannot be fully mechanised in every
case (8.7). Rather than leaving this unmeasured, both are tagged with a
confidence tier at scoring time (High-Confidence / Heuristic-Guidance), so
the ambiguity is visible and analysable rather than silently mixed in with
confidently-assigned categories. The periodic manual/LLM-judge audit
samples specifically from Heuristic-Guidance-tagged responses; the tier
makes the limitation reportable, it does not eliminate it.

A related, distinct gap (added 2026-09-16, 8.7): sampling only from
Heuristic-Guidance-tagged responses cannot detect an IDK-detector *false
negative* — a response that should have triggered a marker (8.6, A.3) but
didn't is tagged High-Confidence, not Heuristic-Guidance, and so is never
sampled by the audit as originally specified. 8.7 now also specifies a
per-language random sample from non-IDK-tagged responses to estimate
this. Until that sample has been run, cross-language IDK/Fabrication-rate
comparisons stay descriptive (10.2).

### 12.4 Source-Language Asymmetry

Every vetted Set A/E source (5.4) is originally authored in US English,
meaning UK and Australian English (Set F) are derived transformations,
not native-authored content (6.1). This is a known constraint on what
"testing English varieties" can mean within this pilot, not a claim that
the transformation is equivalent to native-authored material.

### 12.5 Licence Confirmations (Resolved 2026-09-11)

Two model licence details — Qwen3's exact per-size terms and Gemma 3n's
Prohibited-Use Policy in full (7.5) — were open at the time of drafting.
Both are now confirmed by the study owner and recorded in the Model
Register.

### 12.6 Scope of the Institutional-Criticism Accommodation

The minimal accommodation in 11.5 tests one jurisdiction pair as a
proof of concept; it is not a survey of institutional-criticism tolerance
across jurisdictions generally, and should not be read as one.

### 12.7 Licence Readings Are Not Legal Advice

Every licence and ownership check in this document (5.3, 5.4, 7.2, 7.3)
is a preliminary technical reading performed for research-planning
purposes, not a legal opinion; each "included" decision requires
confirmation before it is relied on for commercial use.

### 12.8 MGSM-Rev2 Custom Harness Task (Resolved 2026-09-08)

MGSM-Rev2 had no existing lm-evaluation-harness integration (9.2, ADR
0008); the harness's built-in MGSM task points to the original, excluded
dataset instead. A custom task definition — `configs/lm_eval_tasks/
mgsm_rev2/` — has now been built and verified against a real
lm-evaluation-harness install for dataset loading, prompt rendering, and
request construction (9.2 has the detail). What remains is end-to-end
verification against a live model backend's actual output — the pilot's
first real run against this task, not a prerequisite for treating the
scaffolding as done — and is tracked as ordinary pre-run verification, not
as an open engineering gap.

### 12.9 MGSM-Rev2 Share-Alike Compliance (corrected 2026-09-16; originally recorded, incorrectly, as "Resolved 2026-09-11")

The Source Register (5.4) flagged MGSM-Rev2's CC BY-SA 4.0 share-alike
obligation as requiring sign-off before any Set E or Set F derivative is
generated from it. This section previously recorded that the study
owner's determination — that this project's own CC BY 4.0 publication
(Data Management Plan, Section 5) satisfies that obligation — was
sufficient, with no separate CC BY-SA 4.0 carve-out applied. **That
determination does not hold under a standard reading of CC BY-SA 4.0
§3(b):** ShareAlike compatibility runs one direction only — BY-SA-licensed
material may be incorporated into a BY-SA-or-later work, but an adaptation
of BY-SA material must itself carry BY-SA 4.0, a later version, or a
licence on Creative Commons' own published Compatible Licenses list; plain
CC BY is not on that list. Publishing the rest of the project under CC BY
does not discharge MGSM-Rev2's obligation for its own derivatives. As with
every licence reading in this document, this is a technical reading for
research-planning purposes, not independent legal advice (12.7) — but it
is the correct default reading absent one, and the previous text asserted
the opposite.

Practical exposure, checked 2026-09-16: every current Set E and Set F row
derives from Set A's *knowledge* domain (MMLU-ProX, MIT-licensed, no
share-alike obligation) — `language_variant_of` for every Set E/F row
traces to an `A-KNOW-*` item, none to an `A-PROC-*` (MGSM-Rev2-sourced)
item. So no existing corpus row is actually out of compliance today. The
live gap is the vendored MGSM-Rev2 TSVs themselves
(`configs/lm_eval_tasks/mgsm_rev2/data/`), redistributed verbatim with no
BY-SA notice, attribution, or changes-indication anywhere in that
directory — required by BY-SA regardless of whether any derivative is
ever built from them. Corrective action, not yet taken: (1) add a
NOTICE/README to that directory carrying CC BY-SA 4.0, attribution to
Google Research, and an indication of changes (temp/format only — no
content alteration); (2) if a Set E or Set F item is ever built from Set
A's procedural (MGSM-Rev2-sourced) domain, that specific item's
redistribution must carry CC BY-SA 4.0 explicitly, not the project's
general CC BY 4.0 default.

### 12.10 llama.cpp Containerisation and GPU Passthrough (Resolved 2026-09-12); vLLM Still Not Built

The Backend Register (9.2) validates llama.cpp and vLLM as suitable
alternate backends, required for Set D (RQ4, tool-calling).
`docker/docker-compose.yml` defines a `llamacpp` service with GPU
passthrough and `--jinja` enabled for tool-calling support (9.2 has the
detail). GPU passthrough end-to-end (`nvidia-container-toolkit` installed
and configured, Docker's `nvidia` runtime registered, the GPU visible
inside the container via `nvidia-smi`) and the tool-calling path itself
are now verified working (2026-09-12): a direct `/v1/chat/completions`
request with a `tools` schema against the registered Qwen3 4B candidate
(`models/model.gguf`) returned a correctly-formed `tool_calls` response.
This work was done in a second, dedicated WSL2 distro (Ubuntu-24.04)
rather than the distro used for other projects, for isolation — a fresh
Docker install and image rebuild were needed there, but the WSL2 mirrored-
networking fix (9.2, `docker-compose.yml`'s header comment) is WSL2-wide
and needed no repeating.

One finding from that verification, not yet acted on: the response
included a separate `reasoning_content` field — Qwen3 4B defaulting to
its "thinking" mode via llama.cpp's chat template. 9.3's Run Parameter
Overrides table already requires Qwen3 to run in non-reasoning ("dialogue")
mode for this pilot; that override is not yet configured for the llama.cpp
backend specifically (only asserted as the intended default generally) and
will need addressing once a Set D task/harness invocation is actually
built — not a blocker to what's verified here, but a concrete follow-up
item, not a hypothetical one.

No vLLM container has been built; since llama.cpp alone is sufficient for
Set D, this is not a blocker to running Set D, but the Backend Register's
"Included" status for vLLM still reflects only that it was checked and
found suitable, not that it is available as a running alternative.

### 12.11 Qwen3 Backend Divergence (identified 2026-09-13)

Found during review, not during design, which is itself worth stating
plainly: Ollama's OpenAI-compatible endpoint was confirmed (2026-09-12) not
to honour the `think` parameter ADR 0010's reasoning-mode conditions
require. The fix adopted — routing all of Qwen3's traffic through
llama.cpp instead (9.2's Backend Register, 9.3's Run Parameter Overrides
table) — solves the reasoning-mode problem but introduces a second,
previously undocumented confound: Qwen3 is now the only tested model
family whose results, across every item family (not only Set D), come
from a different backend than the rest of the Model Register (7.3). A
cross-model difference observed for Qwen3 could reflect llama.cpp's own
serving-stack behaviour (sampling implementation, chat templating) rather
than a genuine model capability difference. This is the same category of
limitation Set D already carries for every model (ADR 0001) — a backend
difference sitting alongside, not replacing, the reasoning-mode difference
ADR 0010 already discusses — just discovered later and covering more of
the design than originally scoped. No mitigation beyond disclosure is
applied in this pilot: building a working `enable_thinking`-equivalent
toggle for Ollama, or running every other model through llama.cpp too for
a fully backend-consistent comparison, are both legitimate options for a
later corpus/protocol version (5.8, 7.5) but are out of scope for
correcting after the fact here. Any RQ1/RQ2/RQ3/RQ6/RQ7 comparison
involving Qwen3 should be read with this caveat attached, not as directly
comparable to same-RQ results for every other model.

### 12.12 llama.cpp Chat-Parser Failure, `qwen3_4b_nonreasoning` (identified 2026-09-18)

During the corpus-v0.3 pilot run, `qwen3_4b_nonreasoning` failed
completely on every one of 3 replicates: `llama-server` returned
`500: "The model produced output that does not match the expected
peg-native format"` on ordinary, unremarkable model output (confirmed on
two unrelated corpus items, one with a free-form multi-sentence preamble
ahead of the final answer despite `enable_thinking:false` being set — the
response *structure*, not the item content, appears to be what breaks the
parser). `--skip-chat-parsing` did not avoid it; `--no-jinja` did, but
also disables `chat_template_kwargs`, silently defeating ADR 0010's
reasoning-mode control — not an acceptable trade. Root-caused to
`llama-server`'s native chat-response parser (`common_chat_peg_parse`,
engaged by `--jinja`), not to a corpus or pipeline defect — full repro
steps are preserved in the run's own handover document
(`results/pilot/20260915T195159Z/`, machine-local, not git-tracked per
the results/* exclusion, 5.7/6 of the Data Management Plan).

**Decision:** rather than chasing this llama.cpp-build-specific bug
further, this one condition is re-run against corpus-v0.3 on the
Windows/WSL2/NVIDIA pipeline (9.2), which uses a different llama.cpp
container image and is confirmed not to hit this failure — cheaper and
more certain than an unverified in-prompt `/no_think` toggle or a
different llama.cpp version, and it closes the gap with real data rather
than leaving it unresolved. This adds one more documented instance of the
same backend-divergence category already disclosed in 12.11 (this one
condition now comes from a *third* distinct llama.cpp build — Windows/
CUDA — rather than the Mac/Metal build the other 8 conditions in this
same pilot run used), not a new category of limitation.

**Deferred action, not yet done:** report this bug upstream to
`ggml-org/llama.cpp`, with the two repro cases and the exact flags
(`--jinja` + Qwen3 chat template + `enable_thinking:false` +
free-form non-English preamble text) already written up in the handover
document referenced above. Logged here specifically so the repro detail
has a git-tracked anchor independent of the machine-local results/
directory it currently also lives in.

---

## 13. Amendment Log

### 13.1 Purpose

Per this document's header, amendments made after the protocol is frozen
are logged here. Everything recorded in this document
up to and including its current version is ordinary pre-freeze drafting —
revision during design, not amendment — and none of it is logged here on
that basis.

### 13.2 Log

| Date | Section changed | Change | Reason | Approved by |
|---|---|---|---|---|
| *(none yet — log begins at first post-freeze amendment)* | | | | |

---

## Appendix A. Corpus Transformation Records

### A.1 Purpose

This appendix holds the governed data that Section 9's procedures produce
— the actual conversion lists, keyword lists, and perturbation log — kept
separate from the procedures that generate and apply them (9.4, 8.6), per
the separation-of-concerns principle established earlier in this document.
Entries here are illustrative starter content for this pilot, not an
exhaustive production list; expanding them is a corpus-version change
(5.8), not an edit to this appendix's existing entries.

### A.2 Set F Conversion Lists

Sourced from: the Wikipedia-compiled "American and British English
spelling differences" article (itself drawing on Oxford Reference's
British/American spelling appendix) for the UK list; the Australian
Government Style Manual (stylemanual.gov.au) for the Australian list,
cross-referenced against the Macquarie/Australian Concise Oxford
Dictionary where the Style Manual itself defers to them.

**US to UK**

| US | UK | Category |
|---|---|---|
| color | colour | -or/-our |
| organize | organise | -ize/-ise |
| center | centre | -er/-re |
| defense | defence | -se/-ce |
| traveled | travelled | single/double consonant |
| aluminum | aluminium | spelling |
| math | maths | abbreviation |
| gray | grey | spelling |
| humor | humour | -or/-our |
| honor | honour | -or/-our |
| labor | labour | -or/-our |
| favor | favour | -or/-our |
| flavor | flavour | -or/-our |
| neighbor | neighbour | -or/-our |
| behavior | behaviour | -or/-our |
| rumor | rumour | -or/-our |
| vapor | vapour | -or/-our |
| vigor | vigour | -or/-our |
| theater | theatre | -er/-re |
| liter | litre | -er/-re |
| fiber | fibre | -er/-re |
| offense | offence | -se/-ce |
| jewelry | jewellery | spelling |
| mold | mould | spelling |
| plow | plough | spelling |

Added 2026-09-15 (corpus-v0.3, alongside the RQ7 corpus expansion, 5.8):
17 more pairs from the same source (the Wikipedia spelling-differences
article), all -or/-our, -er/-re, -se/-ce, or plain-spelling categories
already established above — no new category introduced. Deliberately
excludes several well-known but genuinely context-dependent pairs that
would repeat the exact risk 9.4.2's "public school" bad example warns
against: "program"/"programme" (UK keeps "program" for computer software,
"programme" otherwise), "practice"/"practise" and "license"/"licence"
(UK's noun/verb spelling distinction, not a blanket substitution),
"check"/"cheque" and "curb"/"kerb" (only one specific sense of the US
word converts; the other senses stay identical). These stay excluded from
blind substitution the same way "public school" does, not silently added.

**Removed 2026-09-16 (correctness fix, not an expansion): `tire`→`tyre`
and `meter`→`metre`.** Both had been applied as blind substitutions since
`v0.1`, in violation of 9.4.2's own context-dependence rule — `tire` is
also a verb ("to tire of something"), unaffected by the noun-only
UK/AU spelling change, and `meter` is also a measuring device (a glucose
meter, a parking meter), which UK/AU English keeps as "meter" even where
the unit of length becomes "metre." Checked against the actual corpus,
2026-09-16: no existing Set F triplet (21 items) contains either
converted form, so this was a latent defect in the governed artefact
itself, not a corrupted item — moved here, alongside "public school," for
case-by-case exclusion rather than silently left in the active table for
a future expansion to trip over.

**Added 2026-09-16 — a new category, `-yze/-yse`: `analyze`→`analyse`,
`catalyze`→`catalyse`, `paralyze`→`paralyse` (and their `-d`/`-ing` forms
for `analyze`).** Found via a spot-check of the existing 21 Set F items
against these style guides (m3's native-reader check, done as a partial
self-review rather than by an independent native reader): `F-KNOW-10`'s
UK/AU variants both still read "...added to **catalyze** the formation of
fibrin" — an unconverted US spelling sitting in the same option as a
correctly-converted "colour," left that way because the existing
mechanism's `-ize/-ise` handling only matches the literal substring
"ize," and "catalyze" is spelled with "yze," not "ize," so it was never
matched at all. Left uncorrected in `corpus/v0.3/set_f.csv` itself — that
file is exactly what the pilot run in progress at time of writing is
using, and 5.8's expand-don't-edit discipline means it stays as published,
known-defective, rather than silently patched after being measured
against. Disclosed here as a known `v0.3` erratum — **corrected in
`corpus/v0.4/set_f.csv`** (built 2026-09-16 for the unrelated purpose of
expanding Set E, 5.8), since `v0.4` had not yet been used for any run at
the time the fix was made. The new category is added to the active
tables now so no future Set F build reproduces the same gap.

**Native-reader check completed (2026-09-19).** The self-review spot-
check above was a partial stand-in, not a substitute, for m3's actual
requirement. The study owner has since completed a genuine native-reader
check of the existing 21 Set F triplets against the style guides cited
above, beyond the mechanical `catalyze` fix — confirmed correct. This
closes m3's outstanding sensitivity-validation gap; a fresh check remains
good practice for any future Set F expansion, not a one-off exemption
from it.

**US to Australian**

| US | Australian | Category | Note |
|---|---|---|---|
| color | colour | -or/-our | Follows UK |
| organize | organise | -ize/-ise | Follows UK |
| center | centre | -er/-re | Follows UK |
| acknowledgment | acknowledgement | -ment/-ement | Diverges from plain "follows UK" — the Style Manual's own stated current practice |
| judgment / judgement | judgment (legal contexts only) / judgement (general) | -ment/-ement | A genuine AU-specific rule, not a blanket substitution — legal material keeps "judgment" |
| humor | humour | -or/-our | Follows UK |
| honor | honour | -or/-our | Follows UK |
| labor | labour | -or/-our | Follows UK |
| favor | favour | -or/-our | Follows UK |
| flavor | flavour | -or/-our | Follows UK |
| neighbor | neighbour | -or/-our | Follows UK |
| behavior | behaviour | -or/-our | Follows UK |
| rumor | rumour | -or/-our | Follows UK |
| vapor | vapour | -or/-our | Follows UK |
| vigor | vigour | -or/-our | Follows UK |
| theater | theatre | -er/-re | Follows UK |
| liter | litre | -er/-re | Follows UK |
| fiber | fibre | -er/-re | Follows UK |
| offense | offence | -se/-ce | Follows UK |
| jewelry | jewellery | spelling | Follows UK |
| mold | mould | spelling | Follows UK |
| plow | plough | spelling | Follows UK |

Added 2026-09-15, same 17 pairs and same reasoning as the UK table above
— Australian English follows British spelling for all of these (the
Style Manual states no AU-specific divergence for any of them, unlike
`acknowledgment`/`judgment` above, which do have one).

Context-dependent items excluded from blind substitution (9.4.2): "public
school" (US: state-funded; UK, traditionally: fee-paying independent
school); "program"/"programme", "practice"/"practise",
"license"/"licence", "check"/"cheque", "curb"/"kerb" (added 2026-09-15,
same reasoning — see above); "tire"/"tyre" and "meter"/"metre" (removed
from the active tables 2026-09-16 — see above) — all flagged for
case-by-case exclusion, not correction, matching the worked bad example
already given in 9.4.2.

### A.3 Language-Aware IDK/Fabrication Markers (8.6)

**English** (high confidence): "I don't know," "I'm not sure," "I cannot
verify," "I don't have that information," "I'm not certain."

**German** (reviewed by the study owner, 2026-09-11): "Ich weiß es nicht,"
"Ich bin mir nicht sicher," "Das kann ich nicht bestätigen," "Ich habe
diese Information nicht."

**Swahili** (reviewed by the study owner, 2026-09-11): "Sijui" (I don't
know), "Sina uhakika" (I'm not sure).

**Bengali** (reviewed by the study owner, 2026-09-11): "আমি জানি না" (I
don't know), "আমি নিশ্চিত নই" (I'm not sure).

### A.4 Set E Perturbation Log

The first two rows below are the worked good/bad example pair from 9.4.1
itself (illustrative, not drawn from this project's actual corpus). The
following two rows are real candidates drafted against actual corpus-v0.1
Set A items (`corpus/v0.1/set_e.csv`), reviewed and accepted by the study
owner on 2026-09-09 — `review_status` in that file has been updated from
`candidate` to `accepted` accordingly.

| Source item | Perturbed item | Change type | Review outcome |
|---|---|---|---|
| "What is the powerhouse of the cell?" (gold: mitochondria) | "Which organelle is primarily responsible for generating a cell's chemical energy?" | Concept restatement, not synonym swap | Accepted — logged per 9.4.1's good example |
| "What is the powerhouse of the cell?" (gold: mitochondria) | "What is the energy-generating structure of the cell?" | Near-synonym swap | Rejected at human review — logged per 9.4.1's bad example, not usable as a Set E item |
| `A-KNOW-01-en` (heart's metabolic supply; gold: coronary blood supply) | `E-KNOW-01`: "The cardiac muscle itself needs a constant supply of oxygen and nutrients... What circulatory mechanism actually meets this need?" | Concept restatement — reframes the mechanism rather than rewording "supplied" | Accepted — study owner, 2026-09-09 |
| `A-KNOW-02-en` (evidence of impulse transmission in plants; gold: Mimosa pudica touch response) | `E-KNOW-02`: "Plants have no nervous system, yet some show rapid, coordinated responses to a stimulus. What observation is usually cited as evidence..." | Concept restatement — asks for the evidentiary logic rather than rewording "transmission of impulses" | Accepted — study owner, 2026-09-09 |

**corpus-v0.3 (added 2026-09-16 — these 10 rows existed in
`corpus/v0.3/set_e.csv` since 2026-09-15 but were never logged here,
against 5.5's own requirement; closed as a documentation gap, not a
re-drafting).** Generator: Claude (Anthropic), a general-purpose LLM
distinct from every model under test, per 9.4.1's method — the same
assistant used for the v0.1 pair above. The specific model snapshot used
at drafting time (2026-09-15) was not separately pinned in the original
record; noted here as a gap in provenance precision, not corrected
retroactively, and worth capturing explicitly for any future perturbation
batch. Each German row is a native German perturbation grounded in the
corresponding `A-KNOW-*-de` item's own terminology, not a machine
translation of the English perturbation (corpus-v0.3 README). All 10
reviewed and accepted by the study owner, 2026-09-15.

| Source item | Perturbed item | Change type | Review outcome |
|---|---|---|---|
| `A-KNOW-04-en`/`A-KNOW-04-de` (stabilising-selection scenario; gold: B) | `E-KNOW-05-en`/`E-KNOW-05-de`: "In a population, individuals with extreme trait values... become less common... relative to individuals near the average. What type of natural selection produces this pattern?" | Concept restatement — names the process via its outcome pattern rather than rewording the source MCQ's phrasing | Accepted — study owner, 2026-09-15 |
| `A-KNOW-05-en`/`A-KNOW-05-de` (extinction-vortex vulnerability; gold: A) | `E-KNOW-06-en`/`E-KNOW-06-de`: "What two closely related genetic problems make small populations especially prone to a self-reinforcing decline toward extinction?" | Concept restatement — asks for the two named mechanisms directly rather than rewording "extinction vortex" | Accepted — study owner, 2026-09-15 |
| `A-KNOW-07-en`/`A-KNOW-07-de` (NAD+ regeneration under anaerobic conditions; gold: B) | `E-KNOW-07-en`/`E-KNOW-07-de`: "Which metabolic pathway allows glycolysis to keep producing ATP under anaerobic conditions, by regenerating the NAD+ that glycolysis itself consumes?" | Concept restatement — asks for the pathway by its functional role rather than rewording "this process" | Accepted — study owner, 2026-09-15 |
| `A-KNOW-08-en`/`A-KNOW-08-de` (smallest unit natural selection can change; gold: I) | `E-KNOW-08-en`/`E-KNOW-08-de`: "Evolutionary change happens through shifts in the genetic makeup of a population, not within any single organism... What is the actual unit that changes when natural selection acts?" | Concept restatement — reframes via the population-vs-individual distinction rather than rewording "smallest unit" | Accepted — study owner, 2026-09-15 |
| `A-KNOW-16-en`/`A-KNOW-16-de` (stimulus-intensity encoding; gold: F) | `E-KNOW-09-en`/`E-KNOW-09-de`: "How does the nervous system encode how strong a sensory stimulus is, given that individual action potentials are all the same size?" | Concept restatement — poses the coding-mechanism question directly rather than rewording "varies with" | Accepted — study owner, 2026-09-15 |

**corpus-v0.4 (added 2026-09-16) — 14 new rows, 7 facts x en/de,
targeting RQ6-DE's power floor (10.5).** Generator: Claude (Anthropic),
same method and same assistant as every prior batch. Each source item was
previously unused by any existing Set E or Set F item, keeping the two
sets' signal on distinct underlying facts. **Reviewed and accepted by the
study owner, 2026-09-19** (per 9.4.1's mandatory-human-review
requirement) — `review_status` in `corpus/v0.4/set_e.csv` and the table
below both reflect that sign-off.

| Source item | Perturbed item | Change type | Review outcome |
|---|---|---|---|
| `A-KNOW-06-en`/`A-KNOW-06-de` (sister-chromatid separation timing in meiosis; gold: C, "sister chromatids separate during meiosis I" is the false statement) | `E-KNOW-10-en`/`E-KNOW-10-de`: "...At which division do sister chromatids themselves actually separate?" | Concept restatement — converts a negation-MCQ ("which is NOT true") into a direct positive question about the same underlying fact | Accepted — study owner, 2026-09-19 |
| `A-KNOW-09-en`/`A-KNOW-09-de` (Le Chatelier's principle at equilibrium; gold: A, "removing some of reactant C") | `E-KNOW-11-en`/`E-KNOW-11-de`: "...what change to the reaction mixture would push it to produce more of product C?" | Concept restatement — same scenario and principle, reworded from an MCQ-option-selection format to an open question | Accepted — study owner, 2026-09-19 |
| `A-KNOW-12-en`/`A-KNOW-12-de` (oblique cleavage terminology; gold: H) | `E-KNOW-12-en`/`E-KNOW-12-de`: "...What is this pattern of cleavage called?" | Concept restatement — describes the geometric relationship (angle to the polar axis) rather than naming it, then asks for the term | Accepted — study owner, 2026-09-19 |
| `A-KNOW-13-en`/`A-KNOW-13-de` (acetylcholine vs. intracellular second messengers; gold: C, acetylcholine is the exception) | `E-KNOW-13-en`/`E-KNOW-13-de`: "...does it act as one of these intracellular relay molecules, or does it act at the surface receptor itself?" | Concept restatement — converts a negation-MCQ into a direct either/or question about the same distinction | Accepted — study owner, 2026-09-19 |
| `A-KNOW-14-en`/`A-KNOW-14-de` (fungi excluded from photosynthesis; gold: A, photosynthesis is the exception) | `E-KNOW-14-en`/`E-KNOW-14-de`: "...why can't fungi make their own glucose directly from sunlight and carbon dioxide the way plants do?" | Concept restatement — converts a negation-MCQ into a direct "why not" question about the same underlying fact | Accepted — study owner, 2026-09-19 |
| `A-KNOW-17-en`/`A-KNOW-17-de` (homeotic-gene mutation and segment identity; gold: H, "transformation of one segment into another") | `E-KNOW-15-en`/`E-KNOW-15-de`: "...a segment doesn't simply disappear or duplicate — instead, what actually happens to it?" | Concept restatement — states what the defect is not, then asks what it actually is, rather than rewording "transformation" | Accepted — study owner, 2026-09-19 |
| `A-KNOW-18-en`/`A-KNOW-18-de` (xylem's water-conducting cell types; gold: B, "tracheids and vessel elements") | `E-KNOW-16-en`/`E-KNOW-16-de`: "...What are the two specialised, non-living conducting cell types that make up this tissue?" | Concept restatement — describes the function and property (non-living, conducting) rather than rewording "xylem plant cell types" | Accepted — study owner, 2026-09-19 |

### A.5 Versioning

This appendix is versioned with the corpus (5.8). Every entry added after
the pilot's initial version carries the corpus-version tag it was
introduced under, so a later expansion is traceable to when it happened.

---

## Pending sections
1. Title & Version (formal front matter) — deferred by request
