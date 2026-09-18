# Corpus v0.4

Expands Set E only, per Study Protocol 5.8's versioning rule (expand,
don't edit — `v0.3` is left untouched and still exists as a valid,
citable snapshot, including for the pilot run already in progress against
it at time of writing). Set A, Set B and Set C are carried forward
unchanged. Set F is carried forward with one disclosed correctness fix
(see "Set F erratum fix" below) — not an expansion, a fix to existing
content that had not yet been measured in any completed run.

## Why this release, and why now

Directly motivated by an external review of `docs/STUDY_PROTOCOL.md`
finding that RQ6's German leg (Set E, `corpus_e_de`) was still
mathematically incapable of reaching significance even after `v0.3`
added German data for the first time: McNemar's exact test on `n`
discordant pairs has a best-case (all-discordant-one-direction) floor of
`2*(0.5)^n`, which only drops below 0.05 once `n >= 6`. At `v0.3`'s 5
German items, the floor is `2*(0.5)^5 = 0.0625` — still above 0.05,
reproducing the exact RQ1 failure mode `v0.3` had already fixed once, one
RQ later. This was found and logged in `docs/STUDY_PROTOCOL.md` 10.5, not
caught when `v0.3` was built.

## What changed from v0.3

- **Set E**: grown from 12 to 26 rows (7 new facts × en/de). German count
  goes from 5 to 12 — clears the mathematical floor (`n>=6`) with margin,
  rather than landing exactly on it. All 14 new rows are
  `review_status: candidate`, pending the study owner's sign-off (9.4.1,
  11.4) — drafted by Claude (Anthropic), the same general-purpose LLM
  used for every previous Set E batch, per 9.4.1's method. **Not yet
  usable as confirmatory evidence until reviewed.**
- **Set F erratum fix**: `F-KNOW-10`'s UK/AU variants both still read
  "...added to **catalyze** the formation of fibrin" in `v0.3` — an
  unconverted US spelling, found by a spot-check of the existing 21
  triplets against the cited style guides. Root cause: the conversion
  mechanism's `-ize/-ise` handling matches the literal substring `ize`,
  and "catalyze" is spelled with `yze`, not `ize`, so it was never
  matched. Fixed here (`catalyze` → `catalyse`); the `v0.3` copy is left
  as published, since that file is what the pilot run in progress at
  time of writing is actually using. A new `-yze/-yse` category
  (`analyze`/`catalyze`/`paralyze` and inflections) is added to
  `scoring/data/variety_conversion.json` and Appendix A.2 so no future
  Set F build reproduces the gap.

## Provenance — Set E (14 new rows, 7 facts × en/de)

Each is a concept-restatement perturbation (9.4.1's method) of a
previously-unused Set A knowledge-domain item — specifically one not
already used by an existing Set E or Set F item, keeping each set's
signal on a distinct underlying fact. Generator: Claude (Anthropic), a
general-purpose LLM distinct from every model under test. Each German row
is a native perturbation grounded in the corresponding `A-KNOW-*-de`
item's own terminology, not a machine translation of the English
perturbation — the same discipline `v0.3`'s German Set E batch used.

| Fact | Source item | Gold answer (en / de) |
|---|---|---|
| Meiosis: which division separates sister chromatids | `A-KNOW-06` | Meiosis II / Meiose II |
| Le Chatelier's principle at chemical equilibrium | `A-KNOW-09` | Removing some of product C / Entfernen eines Teils des Produkts C |
| Oblique cleavage in early embryonic development | `A-KNOW-12` | Oblique cleavage / Schiefe Furchung |
| Acetylcholine as a first vs. second messenger | `A-KNOW-13` | First messenger, not a second messenger / Erster Botenstoff, nicht zweiter Botenstoff |
| Why fungi cannot photosynthesise | `A-KNOW-14` | Fungi lack chlorophyll / Pilzen fehlt Chlorophyll |
| Homeotic gene mutation and segment identity | `A-KNOW-17` | One segment is transformed into another / Ein Segment wird in ein anderes umgewandelt |
| Xylem's water-conducting cell types | `A-KNOW-18` | Tracheids and vessel elements / Tracheiden und Gefäßelemente |

Full question text for each is logged in `docs/STUDY_PROTOCOL.md`
Appendix A.4, alongside the change-type note distinguishing it from a
trivial synonym swap (9.4.1's good/bad-example distinction).

## Review status

Same discipline as every previous release: drafted as `candidate`, not
self-certified. These 14 rows are not usable as confirmatory RQ6-DE
evidence until the study owner has reviewed them and `review_status` has
been updated accordingly (5.3/9.4.1/11.4) — do not run a confirmatory RQ6
analysis against this file before that review happens.

## Known scope limitations of this release

- This is a targeted, single-purpose expansion (RQ6-DE's power floor
  only) — not a general corpus growth pass. Set B/C's translation-review
  gap (native-speaker audit, STUDY_PROTOCOL.md 10.5) and RQ7's own power
  question (Set F, 21 triplets) are untouched by this release.
- Bumping every task YAML to `/corpus/v0.4/` (9.7's single-corpus-version-
  per-run discipline) means a full confirmatory run against this version
  re-queries every item family, not only the new Set E rows, even though
  only Set E actually changed in substance. This is the cost of the
  established versioning discipline, not an oversight — see
  `docs/STUDY_PROTOCOL.md` 10.5's no-pooling-across-corpus-versions rule.
