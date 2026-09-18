# Notice — MGSM-Rev2 Data

The TSV files in this directory (`mgsm_en.tsv`, `mgsm_de.tsv`,
`mgsm_sw.tsv`, `mgsm_bn.tsv`) are derived from **MGSM-Rev2**, published by
Google Research, licensed under **Creative Commons Attribution-ShareAlike
4.0 International (CC BY-SA 4.0)**: https://creativecommons.org/licenses/by-sa/4.0/

Original source: MGSM-Rev2 GitHub release (accessed 2026-09-03; see
`docs/STUDY_PROTOCOL.md` Source Register, 5.4). MGSM-Rev2 is itself a
corrected/retranslated successor to MGSM, which is built on GSM8K
(OpenAI, MIT-licensed).

## Changes made

Each language's data was reformatted from its original release layout
into a plain two-column, tab-separated file (`question_text<TAB>gold_answer`,
no header row), for direct loading by this project's custom
`lm-evaluation-harness` task definitions (`mgsm_rev2_direct_*.yaml`, ADR
0008). No question text or gold-answer content was otherwise altered.

## Licence

Per CC BY-SA 4.0 §3(b), this adaptation is distributed under **the same
licence, CC BY-SA 4.0** — not the project's general CC BY 4.0 (see
`docs/STUDY_PROTOCOL.md` 12.9, `docs/DATA_MANAGEMENT_PLAN.md` Section 5,
corrected 2026-09-16). This directory's content is excluded from the
project-wide CC BY 4.0 default stated at the repository root.
