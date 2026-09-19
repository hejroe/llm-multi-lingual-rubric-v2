# Corpus v0.5

Expands Set A and Set F only, per Study Protocol 5.8's versioning rule
(expand, don't edit — `v0.4` is left untouched and still exists as a
valid, citable snapshot). Set B, Set C and Set E are carried forward
unchanged.

## Why this release, and why now

Directly motivated by the corpus-v0.3 pilot run's own RQ7 results, not
scheduled in advance: several conditions sat right on the edge of
significance under Cochran's Q (as low as 0.0498 for one model, before
Holm-Bonferroni correction pushed it back over the 0.05 threshold) —
consistent with a knife-edge power problem at 21 triplets, not a settled
null finding one way or the other.

Checked before building anything, not assumed: of the 18 Set A knowledge
items not yet used by either Set E or Set F, only 2 contained a word from
Appendix A.2's conversion list, and one of those (`A-KNOW-09`) was
already claimed by `v0.4`'s Set E batch. Stretching the existing Set A
pool could not have produced a meaningful RQ7 expansion — a fresh source
pull was the only real option.

## What changed from v0.4

- **Set A**: knowledge domain grown from 39 to 69 items per language
  (en/de/sw/bn) — 276 new rows. Sourced from MMLU-ProX's **chemistry**
  category (HF datasets-server API, offsets 3400-3799), not biology like
  every previous Set A batch — see "Provenance" below for why.
- **Set F**: grown from 21 to 51 US/UK/AU triplets — 60 new rows, derived
  from the 30 new Set A items found to contain a convertible word.

## Provenance — Set A (30 new items x 4 languages = 120 rows)

Sampled from `li-lab/MMLU-ProX` (MIT licence, Source Register 5.4 — the
same already-vetted source every prior Set A batch used), `split=test`,
four consecutive `length=100` batches at `offset=3400,3500,3600,3700`
(2026-09-19). All 400 rows scanned in this range fell in the
**chemistry** category, not biology — the biology category was already
exhausted as far as `v0.3`'s own build had scanned it (up to roughly
offset 3392). This is a deliberate scope decision: the Source Register's
MMLU-ProX vetting (5.4) checked the dataset as a whole, not one category
within it, so drawing on a second MMLU-ProX category is not a new source
requiring fresh vetting — just a different, already-vetted part of the
same one. Content-neutral selection rule, same as `v0.3`'s own Set F
expansion: items were selected only for containing a word from Appendix
A.2's conversion list, not for difficulty or subject appeal. (Chemistry's
physical-chemistry/thermodynamics content is noticeably more
calculation-heavy than the biology conceptual items already in Set A —
worth being aware of as a content-character difference between the two
subsets, not a defect; RQ7 tests variety/spelling bias, which does not
depend on domain difficulty.)

Cross-language alignment verified programmatically before writing
anything, the same way as every previous batch: `question_id`, `answer`,
`answer_index` and `src` all confirmed to match across the en/de/sw/bn
configs at every one of the 400 scanned row positions (0 misaligned).
`source_snapshot_date: 2026-09-19`.

## Provenance — Set F (30 new triplets, 60 rows)

Generated from the 30 new Set A items by the same documented,
case-preserving substitution method as every previous Set F batch
(9.4.2, `scoring/data/variety_conversion.json`). No new conversion-list
entries were needed or added — every word found (`color`, `liter`,
`behavior`, `vapor`, `fiber`, `analyze`/`analyzed`, `aluminum`) was
already in Appendix A.2. Of 53 candidate items found to contain a
convertible word, 24 contained something other than "liter" (all kept,
for word diversity across the set) plus a spread of 6 "liter"-only items
(every third one in scan order, not a contiguous block) — chosen instead
of using all 29 "liter"-only candidates, so this set isn't dominated by
one repeated word. `conversion_list_version: Study Protocol Appendix A.2,
protocol v0.30 (corpus-v0.5 expansion, 2026-09-19)`.

## Known scope limitations of this release

- This is a targeted, single-purpose expansion (RQ7's power problem
  only) — not a general corpus growth pass. Set A's procedural domain,
  and the Set B/C native-speaker translation-review gap (10.5), are both
  untouched here.
- Chemistry's introduction alongside biology in Set A's knowledge domain
  is new as of this release (see Provenance above) — noted here in case
  a future analysis wants to check whether Correct-rate differs by
  underlying subject as well as by language/variety; this release does
  not itself run or report that comparison.
- Bumping every task YAML to `/corpus/v0.5/` (9.7's single-corpus-
  version-per-run discipline) means a full confirmatory run against this
  version re-queries every item family, not only the new Set A/F rows,
  even though Set B/C/E are otherwise unchanged — the same cost `v0.4`'s
  own README already noted for itself.
