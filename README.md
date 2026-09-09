# LLM Multi-Lingual Rubric — Pilot v2

This is the redesigned pilot study following the review and validation of
[`llm-multi-lingual-rubric`](../llm-multi-lingual-rubric) (the original
"Leaderboard Illusion" pre-print and its accompanying code/data). That
original repository is left untouched — this is a fresh project.

## Why this exists

The review found that a substantial share of the original paper's reported
"catastrophic" EN-vs-DE/ES performance collapse was attributable to three
scoring-pipeline bugs (English-only answer matching, reasoning-model
`<think>` traces leaking into scoring, and API/timeout failures folded into
capability scores as neutral zeros) rather than genuine model behaviour. Once
corrected, a real but much smaller gap remained. Separately, we found the
underlying research question — do LLMs answer consistently across languages —
is legitimate and already active in the literature (MMLU-ProX, MGSM,
BorderLines, XLingEval), but no existing work cleanly separates *why* a
cross-lingual gap occurs: resource scarcity, genuine cultural/lexical
absence, model-family artefacts, or measurement noise.

## How to navigate this project

The documentation is deliberately split by concern rather than bundled into
one file. Read in this order:

1. **[`docs/STUDY_PROTOCOL.md`](docs/STUDY_PROTOCOL.md)** — the
   authoritative research design: research questions, hypotheses, corpus,
   languages, models, scoring rubric, procedure, analysis plan,
   contested-claims handling, and limitations. Start here for what this
   study is and how it is designed to answer its questions. Status: DRAFT,
   every section written except the formal title/front matter (Section 1,
   deferred by request).
2. **[`docs/DATA_MANAGEMENT_PLAN.md`](docs/DATA_MANAGEMENT_PLAN.md)** —
   where the data this study produces will live, for how long, and under
   what licence. This project is now under local git version control; its
   remaining open items (no off-machine backup yet, no licence or release
   repository chosen yet) are stated plainly there — none of them block
   running the pilot locally; they matter once results are meant to be
   archived, shared, or cited, not before.
3. **[`docs/adr/`](docs/adr/)** — one-page Architecture Decision Records:
   why a specific design choice was made (backend abstraction, statistical
   test selection, pilot scale, contested-claims scoring, risk framing,
   procedure/record separation, tool-calling modes), each with its
   context and consequences. Read one when you want the reasoning behind
   a specific choice without re-reading the Protocol's full prose.
4. **[`docs/RUBRIC_CARDS.md`](docs/RUBRIC_CARDS.md)** — a practical,
   worked-example companion to the Protocol's Section 8 scoring rubric,
   for anyone actually applying or auditing the scoring by hand.
5. **[`docs/MODEL_REGISTER.md`](docs/MODEL_REGISTER.md)** — the licence,
   ownership, and currency vetting record for every candidate model
   (included or excluded), and the authoritative place the two pending
   licence confirmations (7.5, 12.5) get marked resolved.

Each document versions independently (stated at its own head) but cross-
references the others where a decision or definition lives elsewhere —
none of them duplicate content the Protocol already states authoritatively.

## Design principles carried over from the review

- **Use existing, professionally-translated benchmarks** (MGSM, MMLU-ProX,
  and IrokoBench's AfriMGSM for genuinely low-resource languages) rather than
  a bespoke, hand-translated corpus — this is what `lm-evaluation-harness`
  gives us for free, already implemented per-language.
- **Raw model responses are immutable and rubric-agnostic.** Store once,
  score any number of ways, always versioned. (This is exactly the pattern
  used ad hoc during the review — re-scoring the same raw JSONL under
  different rubrics without re-querying any model.)
- **Untrusted/third-party code runs in a container**, never directly against
  the host — see `docker/`.
- **Multi-axis scoring**: capability, reliability (infrastructure failures),
  and consistency (for contested/perspective-dependent items) are reported
  separately, never collapsed into one number.

## Prerequisites

- WSL2 with an Ubuntu LTS distro (already set up).
- Docker Engine installed *inside* that WSL2 distro (not Docker Desktop):
  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER   # then restart your WSL2 session
  ```
- Ollama running on Windows, with at least one model already pulled
  (e.g. `ollama pull llama3:8b`).

## First run

1. Build the image:
   ```bash
   cd docker
   docker compose build
   ```
2. Confirm the container can actually reach Ollama before trusting anything else:
   ```bash
   docker compose run --rm eval bash scripts/check_ollama_connectivity.sh
   ```
   If this fails, see the troubleshooting notes printed by the script itself
   before going any further.
3. Run a tiny smoke test (5 items, one domain, one registered model):
   ```bash
   docker compose run --rm eval lm_eval --model local-chat-completions \
     --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
     --tasks mmlu_prox_en_biology \
     --limit 5 \
     --output_path /results/smoke_test_mmlu_prox_en
   ```
   The model used here is one of the registered candidates
   (`docs/MODEL_REGISTER.md`), within the size band Protocol 7.4 sets. The
   task targets MMLU-ProX, which has a working stock harness task
   (Protocol 9.2). `host.docker.internal` is used because Ollama runs
   natively on Windows in this project's setup, not as a containerised
   service (see `docker/Dockerfile`'s header comment and the
   `extra_hosts` entry in `docker-compose.yml`; Protocol 9.2 documents
   this).
4. A parallel smoke test for MGSM-Rev2 (custom task, ADR 0008), once the
   corpus exists beyond Appendix A's starter content:
   ```bash
   docker compose run --rm eval lm_eval --model local-chat-completions \
     --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
     --include_path /configs/lm_eval_tasks \
     --tasks mgsm_rev2_direct_de \
     --limit 5 \
     --output_path /results/smoke_test_mgsm_rev2_de
   ```
   See `configs/lm_eval_tasks/mgsm_rev2/README.md` for what has and hasn't
   been independently verified about this task yet.
5. Set D (RQ4, tool-calling) is routed to llama.cpp instead of Ollama —
   see ADR 0001 and Protocol 9.2. Bring the `llamacpp` compose service up
   first (a GGUF model must be placed in `models/` beforehand — see
   `models/README.md`), then check connectivity before running anything:
   ```bash
   docker compose up -d llamacpp
   docker compose run --rm eval bash scripts/check_llamacpp_connectivity.sh
   ```
   Only one backend can hold the GPU at a time on this project's target
   hardware (8GB VRAM) — stop Ollama-serving runs before starting a Set D
   run, not the other way round (Protocol 9.2).
6. Results land in `results/smoke_test_mgsm_de/` on the Windows side, under
   this folder — nothing needs copying out of WSL2 or the container manually.

## Status

This is scaffolding plus a complete draft protocol, produced for review
before any real evaluation run. Nothing has been executed yet —
`docker compose build` and every step under First Run needs to be run by
you inside WSL2, since the bridge this project folder is reached through
does not have Docker available and cannot drive it directly.

The Study Protocol is complete apart from its own front matter (Section 1,
deferred by request); its three pre-registration values (alpha, RQ6
threshold, primary language) are confirmed by the study owner (Protocol
10.3, 10.5). Two supporting pieces of infrastructure exist: a custom
lm-evaluation-harness task for MGSM-Rev2
(`configs/lm_eval_tasks/mgsm_rev2/`, ADR 0008) and a containerised
llama.cpp backend with GPU passthrough for Set D
(`docker/docker-compose.yml`'s `llamacpp` service), both documented at
Protocol 9.2 and Limitations 12.8/12.10. Neither has been run end-to-end
against a live model yet — that is ordinary pre-run verification,
remaining before the pilot's first real run.

Corpus/item authoring has started: `corpus/v0.1/` (2026-09-08) holds the
first real corpus release across all six item families; `corpus/v0.2/`
(2026-09-09) supersedes v0.1's Set B and Set C only — expanded from one
fact each to ten, every fact independently source-verified, and
translated into German, Swahili and Bengali (candidate translations,
pending review). Each version's own README states what's verified, what's
a candidate pending review, and what's a scoping choice rather than an
oversight. This folder is under local git version control (`.gitignore`
excludes `results/` at volume); as of 2026-09-09 it holds four commits
with a clean working tree (`DATA_MANAGEMENT_PLAN.md` Section 3). Known
open items are tracked where they arise rather than repeated here: see
`STUDY_PROTOCOL.md` Section 12 (Limitations) and
`DATA_MANAGEMENT_PLAN.md` Sections 3, 5, and 6.
