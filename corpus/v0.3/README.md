# Corpus v0.3

Expands Set A, Set B, Set E and Set F, per Study Protocol 5.8's
versioning rule (expand, don't edit — `v0.2` is left untouched and still
exists as a valid, citable snapshot). Set C is carried forward unchanged
(the same treatment Set A/E/F received in `v0.2`, mirrored here).

## Why this release, and why now

Directly motivated by the first full pilot run's own findings
(`docs/PILOT_RESULTS.md`), not scheduled in advance:

- **RQ1 was mathematically incapable of significance** at 3 paired items
  per domain/language — McNemar's exact test on ≤3 discordant pairs
  cannot reach p<0.05 regardless of the true effect size (2×(½)³=0.25 is
  the best case). This is a hard floor, not a power inconvenience.
- **RQ7 had exactly one triplet** — Cochran's Q needs variation across
  multiple items to say anything at all.
- **RQ6 had zero German (primary-language, 10.5) data** — structurally
  unable to report anything for any model, regardless of scale
  elsewhere.
- RQ2 already showed real effects at the `v0.2` scale (10 facts, 6 of 9
  model/condition results significant) but left several borderline cases
  (p=0.06–0.45) that more data could plausibly resolve either way.

## What changed from v0.2

- **Set A**: knowledge domain grown from 3 to 39 items per language
  (en/de/sw/bn), procedural domain from 3 to 23 — 248 rows total (up
  from 24).
- **Set B**: 6 new jurisdiction-contingent facts (UK vs Germany), 10 to
  16 facts — 192 rows total (up from 120).
- **Set E**: 10 new perturbed-twin items, including 5 in German (the
  first German Set E data this project has had) — 12 rows total (up
  from 2).
- **Set F**: 20 new US/UK/AU triplets, 1 to 21 — 42 rows total (up from
  2). Appendix A.2's conversion list itself was expanded (17 more word
  pairs) to actually find enough convertible content in real item text.

## Review status

Every new row in this release was drafted as `review_status: candidate`,
not `verified`/`accepted`/`translation-reviewed` — 5.3/9.4.1/11.4 all
treat human sign-off (the study owner's, specifically) as the step that
makes an item usable evidence, not merely present in the corpus. The new
items were built by an AI assistant (Claude) acting on the study owner's
explicit direction ("I actually think that you are well placed to do all
of this and I will simply review the final work"), with each Set B fact
backed by real web research against a cited primary source (not
fabricated), and each Set E/F item built via exactly the documented
mechanical/paraphrase methods 9.4.1/9.4.2 specify.

**That review has since been completed**: the study owner (hejroe,
2026-09-15) reviewed all of corpus-v0.3, "paying special attention to
the new items," with no amendments or comments. `review_status` in
`set_b.csv`/`set_e.csv` and the Ethics Register sign-off column (11.4)
both reflect that sign-off — `verified`/`translation-reviewed` (Set B)
and `accepted` (Set E), matching v0.1/v0.2's own already-reviewed
content, not left as `candidate` after the review that word was
signalling had actually happened.

## Provenance — Set A (knowledge domain, 36 new items across 4 languages)

Sampled from `li-lab/MMLU-ProX` (MIT licence, Source Register 5.4 — the
same already-vetted source `v0.1` used) via the HF datasets-server API,
`category=biology`, `split=test`, two batches (`offset=3170,length=23`
and 13 further rows selected from a `offset=3193,length=200` scan for
items containing a documented US/UK spelling difference, needed for the
Set F expansion below — a content-neutral selection rule, not one based
on question difficulty or answer correctness). Cross-language alignment
verified programmatically (`question_id`, `answer`, `answer_index`,
`src` match across all 4 language configs for every row) before writing
to `set_a.csv`. `source_snapshot_date: 2026-09-15`.

## Provenance — Set A (procedural domain, 20 new items across 4 languages)

Sampled from the already-vendored MGSM-Rev2 TSVs
(`configs/lm_eval_tasks/mgsm_rev2/data/`, CC BY-SA 4.0, Source Register
5.4), rows 4–23 (0-indexed 3–22) of each language file — the same
source `v0.1`'s first 3 items already used, just further into the
already-present 250-row files. Row-aligned across languages by line
number (no header row in the source TSVs).

## Provenance — Set F (20 new triplets)

Generated from the 20 Set A knowledge items found (via a case-preserving,
suffix-preserving programmatic substitution — `scoring/data/
variety_conversion.json`) to contain a word from Appendix A.2's US/UK/AU
spelling-conversion list, restricted throughout to the same
context-independent categories 9.4.2 already establishes as safe to
automate (a plain spelling swap, never the semantic/vocabulary kind of
substitution the "public school" bad example warns against). Every
conversion is logged with the exact before/after word pairs it applied;
`F-KNOW-01` (the one `v0.1` item) is carried forward unchanged.
`conversion_list_version: Study Protocol Appendix A.2, protocol v0.28
(corpus-v0.3 expansion, 2026-09-15)`.

## Provenance — Set E (10 new items, 5 English + 5 German)

Perturbed twins of 5 Set A knowledge items (concept restatement per
9.4.1's method — verified against the good/bad-example distinction there,
not a synonym swap), generated by Claude (a general-purpose LLM distinct
from every model under test, satisfying 9.4.1's "documented, disclosed
method" requirement) in both English and German directly, grounded in
the actual German technical terminology already present in the
corresponding Set A `-de` items (not machine-translated from the English
perturbation after the fact). `set_e.csv` gained a `language` column
this release (previously implicit/English-only); a new `corpus_e_de`
harness task was added to match.

## Provenance — Set B (6 new facts, 72 rows across 4 languages)

Each fact genuinely researched via web search against a citable primary
source, following 5.3's discipline exactly:

| Fact | UK/England figure | Germany figure | Primary sources |
|---|---|---|---|
| Minimum private-company share capital | No statutory minimum | €25,000 | Companies Act 2006; GmbHG, s.5(1) |
| General civil contract claim limitation period | 6 years (England & Wales) | 3 years | Limitation Act 1980, s.5; BGB, s.195 |
| GDPR child digital-consent age | 13 | 16 | Data Protection Act 2018, s.9 / UK GDPR Art.8; BDSG, s.24 / GDPR Art.8 |
| Organ donation consent system | Opt-out/deemed consent (England) | Opt-in/Entscheidungslösung | Organ Donation (Deemed Consent) Act 2019; Transplantationsgesetz |
| Compulsory national ID card possession | No legal requirement | Required from age 16 | Identity Documents Act 2010; Personalausweisgesetz |
| Minimum blood donation age | 17 (England) | 18 | NHS Blood and Transplant eligibility criteria; Transfusionsgesetz |

Jurisdiction labels are deliberately precise, not loosely "the United
Kingdom" where the actual law is narrower — matching `v0.2`'s own
established discipline (e.g. `B-CRIM-01`'s "England and Wales", not
"UK"):

- **Contract limitation** is England & Wales specifically — Scotland has
  its own Prescription and Limitation (Scotland) Act 1973 with different
  periods.
- **Organ donation** is England specifically — Wales (2015) and Scotland
  (2021) separately enacted their own, differently-named opt-out laws;
  citing the England Act for a claim about "the United Kingdom" would
  have been imprecise even though the practical outcome is now similar
  across Great Britain.
- **Blood donation age** is England specifically — NHS Blood and
  Transplant is an England-specific body; this is also the
  weakest-sourced fact in this release (administrative eligibility
  criteria, not primary legislation) — flagged here rather than glossed
  over, per 5.3's ownership/provenance test.
- **Organ donation, live context**: a cross-party bill to move Germany
  to an opt-out system was under active Bundestag debate as of September
  2026 but had not been enacted — this item reflects the law as it
  currently stands, not the pending proposal. Worth re-checking before
  this item is relied on for a future run, given the live debate.

All translations (DE/SW/BN) are machine-drafted by Claude, grounded in
the specific statute/citation being described, not a generic translation
pass — but, per the Review status section above, not yet independently
reviewed.

## Known scope limitations of this release

- Set C is unchanged — RQ3's descriptive design already produced a
  decisive result (0.0% `Flagged-Uncertain-Appropriately` across every
  tested condition) at `v0.2`'s scale, so expanding it wasn't
  prioritised alongside the RQs that were actually blocked.
- Set F's own `variety` field still has no accompanying `language`
  field in the common schema (5.6) — a pre-existing cosmetic gap
  (`docs/PILOT_RESULTS.md` Section 10, item 3), not something this
  release fixes.
- The corpus-wide item count roughly doubled — expect pilot runtime to
  scale accordingly on whatever hardware the next full run uses.

## Schema note

No schema changes except `set_e.csv` gaining a `language` column (see
Set E provenance above). Every other file's columns are unchanged from
`v0.1`/`v0.2` (Protocol 5.6).
