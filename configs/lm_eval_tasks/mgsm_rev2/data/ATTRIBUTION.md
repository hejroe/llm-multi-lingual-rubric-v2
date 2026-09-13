# MGSM-Rev2 — Vendored Data Attribution

Source: https://github.com/google-research-datasets/MGSM-Rev2
Retrieved: 2026-09-08 (main branch)
Licence: CC BY-SA 4.0 (see upstream README, MGSM-Rev2-upstream-README.md,
in this folder)

Paper introducing this dataset: "Mind the Gap... or Not? How Translation
Errors and Evaluation Details Skew Multilingual Results"
https://arxiv.org/abs/2511.05162

Vetted and included per this project's Source Register:
docs/STUDY_PROTOCOL.md Section 5.4.

CC BY-SA 4.0 is a share-alike licence: any derivative work built from
these files (this project's Set E perturbed twins, Set F variety
transforms) would ordinarily carry that obligation forward. Resolved
2026-09-11: the study owner has determined that this project's own open
publication under CC BY 4.0 (docs/DATA_MANAGEMENT_PLAN.md Section 5)
satisfies that obligation, so no separate CC BY-SA 4.0 carve-out is
applied to MGSM-Rev2-derived items — see docs/STUDY_PROTOCOL.md Section
12.9 and the Source Register (5.4) for the full determination. As with
every licence reading in this project, this is the study owner's own
determination, not independent legal advice (12.7).

Files:
- mgsm_de.tsv, mgsm_sw.tsv, mgsm_bn.tsv, mgsm_en.tsv — question/answer
  pairs, tab-separated, no header row, 250 rows each.
- replaced_questions.json — per-language list of item indices whose
  question text was corrected from the original MGSM (provenance record).
- MGSM-Rev2-upstream-README.md — the dataset's own README, unmodified.
