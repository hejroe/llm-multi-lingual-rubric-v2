# Data Management Plan

**Status:** DRAFT
**Version:** 0.5
**Last updated:** 2026-09-11
**Companion to:** `STUDY_PROTOCOL.md` (referenced there at 5.7, 8.8, 9.7)

## 1. Purpose and Scope

This plan states where the artefacts this study produces live, who is
responsible for them, how long they are kept, and what becomes shareable
and under what licence. The Study Protocol defines what data is collected
and how (Sections 5, 8, 9); it does not say where that data lives, for how
long, or how it becomes reviewable or citable outside this project folder
— that gap is what this document closes.

## 2. Data Inventory

| Artefact | Produced by | Format | Approx. volume at pilot scale | Personal data? | Sensitive-topic data? |
|---|---|---|---|---|---|
| Corpus items (Sets A–F) | Sourcing and transformation procedures (5, 9.4) | CSV, one row per item per the common schema (5.6) — corrected 2026-09-13, this previously said JSON/JSONL, stale relative to `corpus/v0.1/`/`corpus/v0.2/`'s actual format | Low hundreds of items at pilot scale (5.1/6.5/7.1's starting scale) | No | Only the Ethics Register subset (below) |
| Raw model responses | Harness runs against each candidate model (7.3/9.3) | JSONL, one line per (item, model, language, condition) per 9.6's run-level provenance capture | Scales with corpus × models × languages × conditions; still pilot scale | No | No |
| Scored/annotated data | Rubric application (Section 8) over raw responses | JSONL/CSV, rubric category and overlay-axis tags appended to each response record | Same row count as raw responses | No | No |
| Amendment Log (13) and Ethics Register (11.4) entries | Manual, by the study owner | Markdown tables within `STUDY_PROTOCOL.md` | Small, append-only | No | Yes — sovereignty disputes and institutional-criticism/lese-majeste items (Protocol Section 11); not personally identifiable, but politically/ethically sensitive by subject matter, which is why Section 11's review gate exists |
| Analysis outputs (10) | Statistical analysis over scored data | Regenerable via `analysis.cli`; first written results report produced 2026-09-14 (`docs/PILOT_RESULTS.md`) | Small | No | No |

No participant or human-subject data is collected at any stage. All corpus
items are drawn from, or derived from, existing public benchmarks and
sources (5.4) or public institutional/legal documents (11.3). This plan
therefore does not carry a personal-data or consent section beyond noting
that absence here — the one row above marked sensitive-topic is a
subject-matter sensitivity, not a personal-data one, and is governed by
Protocol Section 11, not by this plan.

## 3. Storage During the Project

Working copies live in this project folder (`llm-multi-lingual-rubric-v2/`),
under `results/` for run outputs (per the existing `README.md`) and
`corpus/` for corpus items (`corpus/v0.1/`, `corpus/v0.2/`, versioned per
5.8) — corrected 2026-09-13, this previously said a corpus directory was
"to be created under `data/`... not yet built," stale relative to both
versions actually existing at the repository root since 2026-09-08, under
`corpus/`, not `data/` (the latter holds only `models/`'s GGUF weights and
`scoring/data/`'s machine-readable marker/conversion lists, unrelated to
the corpus itself).

Version control: a local git repository is initialised in this project
folder (`git init`, default branch `main`, with a `.gitignore` excluding
`results/` at volume per Section 6 below), with a clean working tree as
of 2026-09-11. Running git through the Cowork device bridge can leave a
stale `.git/index.lock` behind, since the bridge's mounted filesystem
cannot delete files by default; clearing that lock, or running git from
a native shell on the host machine instead, resolves it without
affecting repository integrity. GitHub and GitLab remotes are confirmed
(Section 5) as the public-release and backup destination (Section 6) —
local version control alone would otherwise be enough to make every
run's corpus/rubric/code version reconstructable per the versioning
clauses already in the Protocol (5.8, 7.5, 8.8, 9.7); those version
numbers are not reproducibility guarantees on their own without a
matching commit to
point to.

Backup: no automated backup is currently configured. See Section 6 — this
is a genuine open item, not something this plan resolves by stating it.

## 4. Documentation and Metadata

Every corpus item carries the provenance and temporal metadata fields
defined in 5.7 (source, retrieval date, licence, item family). Every run
carries the provenance fields defined in 9.6 (backend, model identifier,
run parameters, timestamp). This plan, the Study Protocol, and the ADR log
(`docs/adr/`) together serve as the project's metadata; no separate data
dictionary is maintained outside the schema already defined in 5.6.

## 5. Data Sharing and Licensing

Corpus items derived from share-alike-licensed sources (5.3/5.4) carry
that obligation forward to any derivative Set E/F items built from them
(9.4) — stated in the Protocol and repeated here because it governs what
CAN be shared, not only what should be.

Licence for this project's own original content, confirmed by the study
owner (hejroe, 2026-09-11) and applied to the repository: CC BY 4.0 for
documentation and data, MIT for code (repository root `LICENSE`).

MGSM-Rev2's CC BY-SA 4.0 share-alike obligation (Source Register,
Protocol 5.4) required sign-off before any Set E or Set F derivative
built from it could be generated or released. **Corrected 2026-09-16
(Protocol 12.9):** this project's general CC BY 4.0 publication does not
discharge that obligation — BY-SA 4.0's ShareAlike clause requires an
adaptation to itself carry BY-SA 4.0, a later version, or a Creative
Commons-listed Compatible License, and plain CC BY does not qualify. No
current corpus item is actually affected (every existing Set E/F row
derives from the MIT-licensed MMLU-ProX side of Set A, not MGSM-Rev2), but
the vendored MGSM-Rev2 TSVs (`configs/lm_eval_tasks/mgsm_rev2/data/`)
still require their own BY-SA 4.0 notice and attribution, independent of
whether any derivative is built from them, and any future MGSM-Rev2-derived
Set E/F item must carry CC BY-SA 4.0 explicitly rather than the project's
general CC BY 4.0 default.

Planned release point: alongside eventual publication or public
write-up, not before. During the pilot the project remains private.

Repository for public release, confirmed by the study owner (2026-09-11):
GitHub and GitLab, both mirroring the same history. This differs from
OSF/Zenodo, which additionally offer a versioned deposit with a citable
DOI — the study owner has confirmed GitHub/GitLab as sufficient for now;
a DOI-citable deposit remains available later if formal citation is
needed.

## 6. Retention, Backup, and Long-Term Preservation

Retention period: for the life of the project, plus a minimum of five
years post-publication, or indefinitely if publicly deposited. The
five-year figure follows common institutional research-data-retention
practice and is stated here as a working assumption, not a rule specific
to this project.

Backup, confirmed by the study owner (2026-09-11): the GitHub and GitLab
remotes (Section 5) serve as off-machine backup for corpus, code, and
protocol text, alongside the local machine copy. Raw model responses
(Section 9) are the most expensive artefact to regenerate, since
regenerating them requires live inference runs, and they do not belong in
git history at volume; a separate backup destination for the raw-response
JSONL files, once runs exist to back up, remains open.

Responsible party: the study owner. This project has no other named
collaborators at pilot stage, beyond the named reviewer(s) assigned to the
Ethics Register (11.4), whose responsibility is limited to that sign-off.

## 7. Roles and Responsibilities

- **Study owner** — data collection, storage, retention decisions, and the
  eventual release decision.
- **Named reviewer(s)** (11.4) — sign-off on contested-claims items only;
  not general data management.

## 8. Versioning

This plan versions independently of the Study Protocol, but should be
reviewed whenever 5.8, 7.5, 8.8, or 9.7 change in a way that affects what
data exists or how it is produced.
