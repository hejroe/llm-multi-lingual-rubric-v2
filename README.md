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
   where the data this study produces lives, for how long, and under what
   licence. This project is under local git version control with GitHub
   and GitLab remotes, which serve as both the public-release repository
   and off-machine backup (DMP Sections 5, 6). The licence (CC BY 4.0 for
   documentation/data, MIT for code, repository root `LICENSE`) is
   applied.
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
   (included or excluded). All candidate models are licence-confirmed
   (7.5, 12.5).

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
- **WSL2 networking, set up on the Windows host before anything below will
  actually connect** (added 2026-09-13 — previously only documented inside
  `docker-compose.yml`'s header comment and the connectivity-check
  script's own troubleshooting output, discovered only by hitting the
  failure first):
  - `%UserProfile%\.wslconfig` needs `[wsl2]` with `networkingMode=mirrored`
    (then `wsl --shutdown` and restart your distro).
  - Ollama needs `OLLAMA_HOST=0.0.0.0` set (Windows environment variable,
    then restart Ollama) so it listens on more than just `localhost`.
  - Windows Firewall needs an inbound rule allowing TCP port 11434 (Ollama's
    default port) from the WSL2 virtual adapter.
  - If step 2 below still fails after this, its own printed troubleshooting
    output has the exact diagnostic commands.
- Ollama running on Windows, with at least one model already pulled
  (e.g. `ollama pull llama3.2:1b` — the model the smoke tests below
  actually use).
- For Set D (tool-calling, step 5 below) or any llama.cpp-backed run only:
  the NVIDIA Container Toolkit installed and configured for Docker GPU
  passthrough (`scripts/check_llamacpp_connectivity.sh`'s own
  troubleshooting output has the exact check). Not needed for the
  Ollama-backed smoke tests or Phase 1 of the full pilot.

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
3. Run a tiny smoke test (5 items, one domain, one registered model) —
   verified passing 2026-09-12:
   ```bash
   docker compose run --rm eval lm_eval --model local-chat-completions \
     --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
     --apply_chat_template \
     --tasks mmlu_prox_en_biology \
     --limit 5 \
     --output_path /results/smoke_test_mmlu_prox_en
   ```
   `--apply_chat_template` is required — without it, this lm-eval-harness
   version rejects `local-chat-completions` with an assertion error; not
   mentioned in this project's earlier documentation, found only once this
   command was actually run. The model used here is one of the registered candidates
   (`docs/MODEL_REGISTER.md`), within the size band Protocol 7.4 sets. The
   task targets MMLU-ProX, which has a working stock harness task
   (Protocol 9.2). `host.docker.internal` is used because Ollama runs
   natively on Windows in this project's setup, not as a containerised
   service (see `docker/Dockerfile`'s header comment and the
   `extra_hosts` entry in `docker-compose.yml`; Protocol 9.2 documents
   this).
4. A parallel smoke test for MGSM-Rev2 (custom task, ADR 0008) — verified
   passing 2026-09-12:
   ```bash
   docker compose run --rm eval lm_eval --model local-chat-completions \
     --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
     --apply_chat_template \
     --include_path /configs/lm_eval_tasks \
     --tasks mgsm_rev2_direct_de \
     --limit 5 \
     --output_path /results/smoke_test_mgsm_rev2_de
   ```
   See `configs/lm_eval_tasks/mgsm_rev2/README.md` for what has and hasn't
   been independently verified about this task yet. This project's own
   curated corpus rows run through `configs/lm_eval_tasks/corpus_*/`
   instead (ADR 0009) — see each family's own README there.
5. Set D (RQ4, tool-calling) is routed to llama.cpp instead of Ollama —
   see ADR 0001 and Protocol 9.2. Bring the `llamacpp` compose service up
   first (a GGUF model must be placed in `models/` beforehand — see
   `models/README.md`), then check connectivity before running anything:
   ```bash
   docker compose up -d llamacpp
   docker compose run --rm eval bash scripts/check_llamacpp_connectivity.sh
   ```
   Verified working end-to-end 2026-09-12, including a real tool-calling
   request against the registered Qwen3 4B candidate (Limitations 12.10) —
   done in a dedicated second WSL2 distro for isolation from other
   projects sharing the same machine (the `.wslconfig` mirrored-networking
   fix this whole pipeline depends on is WSL2-wide, so it needed no
   repeating there). Only one backend can hold the GPU at a time on this
   project's target hardware (8GB VRAM) — stop Ollama-serving runs before
   starting a Set D run, not the other way round (Protocol 9.2).
6. Results land in `results/smoke_test_mmlu_prox_en/` and
   `results/smoke_test_mgsm_rev2_de/` (corrected 2026-09-13 — this
   previously named a directory, `smoke_test_mgsm_de/`, that neither
   smoke test above actually writes to) on the Windows side, under this
   folder — nothing needs copying out of WSL2 or the container manually.

## Running the full pilot

Once the smoke tests above pass, the actual pilot run (full corpus, all
registered candidates, 9.3's replication) is scripted rather than run by
hand — see `scripts/README.md` for `run_pilot_ollama_models.sh` (every
Ollama-backed candidate) and `run_pilot_qwen3_llamacpp.sh` (both Qwen3
sizes, routed through llama.cpp for genuine reasoning-mode control, ADR
0010). Both write into `results/pilot/`, which stays out of git
(`.gitignore`) regardless of scale — only the scripts, tasks, and scoring
code that produce and consume that data are version-controlled; the raw
responses themselves are backed up separately per
`DATA_MANAGEMENT_PLAN.md` Section 6. Once both phases finish,
`scoring/score_pilot_run.py` scores every run in one pass. On modest
hardware, `scripts/monitor_thermals.ps1` is worth running alongside —
see its own entry in `scripts/README.md` for why.

**Before running either phase, stage every model it needs** (added
2026-09-13 — previously undocumented, so a Phase 1 run hit an Ollama
"model not found" error one model at a time rather than failing fast with
a clear list up front):

- Ollama (Phase 1, `run_pilot_ollama_models.sh`): pull all five —
  `ollama pull llama3.2:1b`, `smollm2:1.7b`, `gemma3n:e2b`, `llama3.2:3b`,
  `phi4-mini`.
- llama.cpp (Phase 2, `run_pilot_qwen3_llamacpp.sh`): place both Qwen3
  GGUF files in `models/` — `model_qwen3_1.7b.gguf` and
  `model_qwen3_4b.gguf` — see `models/README.md` for where to get each
  one (including reusing Ollama's own already-downloaded blob for the
  1.7B size, rather than a second download).

## Status

The Study Protocol is complete apart from its own front matter (Section 1,
deferred by request); its three pre-registration values (alpha, RQ6
threshold, primary language) are confirmed by the study owner (Protocol
10.3, 10.5).

As of 2026-09-12, this is no longer scaffolding: the full pipeline has run
end-to-end against a live model for the first time.

- **Docker/Ollama pipeline**: built and verified (`docker compose build`,
  both connectivity checks, both README smoke tests below all pass against
  a live `llama3.2:1b`). Getting there required fixing a real WSL2/Docker
  networking gap — see `docker-compose.yml`'s header comment.
- **Custom lm-evaluation-harness tasks**: MGSM-Rev2
  (`configs/lm_eval_tasks/mgsm_rev2/`, ADR 0008), plus — found necessary
  only once real runs were inspected — tasks reading every other corpus
  set directly (`configs/lm_eval_tasks/corpus_{a,b,c,e,f}/`, ADR 0009),
  since neither the stock MMLU-ProX task nor MGSM-Rev2 actually ran
  against this project's own curated corpus rows otherwise.
- **The scoring rubric (Section 8)** is implemented as tested code
  (`scoring/`, rubric-v0.3), not just prose — 50 tests, each keyed to a
  specific worked example from `RUBRIC_CARDS.md` or the Protocol itself.
- **The I/O layer** (`scoring/io.py`) joins harness `--log_samples`
  output to the rubric, with 9.6's run-level provenance stamping.
- **The Section 10 statistical analysis pipeline** (`analysis/`) is
  implemented: McNemar's exact test, Clopper-Pearson intervals, Cochran's
  Q, Holm-Bonferroni correction, the behavioural response profile (10.2),
  the reliability metric (10.4), and RQ1/RQ2/RQ3/RQ6/RQ7 wired to scored
  data (RQ4 awaits Set D infrastructure, below).
- **GPU passthrough and Set D's tool-calling path** are verified working
  (Limitations 12.10) — done in a second, dedicated WSL2 distro
  (Ubuntu-24.04) for isolation from other projects sharing this machine.

See `requirements.txt` for the local Python dependencies `scoring/` and
`analysis/` need to run directly (`pip install -r requirements.txt`,
`python -m pytest`, `python -m scoring.cli`, `python -m analysis.cli`) —
separate from the `docker/` image, which only runs lm-evaluation-harness
itself.

**Status, 2026-09-14: the first full pilot run has completed** — all
seven registered candidate models (nine conditions, counting Qwen3's
reasoning-mode split, ADR 0010), full corpus-v0.2 scale, 3-way replication
(Protocol 9.3), 6,156 scored responses. See
**[`docs/PILOT_RESULTS.md`](docs/PILOT_RESULTS.md)** for the actual
findings (RQ1-RQ3, RQ6, RQ7, reliability, and Infrastructure-Failure rate,
per model) and known caveats. Getting there required fixing real
data-integrity and analysis-design bugs invisible until real multi-model
data existed — see that document's own Section 10 and the git history
around 2026-09-13/14 for what was found and fixed (stale duplicate run
data, Qwen3 provenance, and pooling every model together before this pass
split the analysis per model, per 10.2's own reporting grain).

**What's still open**: the corpus's current scale leaves RQ1 and
especially RQ7 statistically inconclusive (n=3 and n=1 pairs
respectively — Limitations 12.2), and RQ6 has no German (primary
language) Set E data yet to report against at all. `PILOT_RESULTS.md`
Section 12 has the full list of recommended next steps. A known,
documented gap (`scoring/io.py`'s module docstring): stock
lm-eval-harness doesn't surface a per-item error/timeout signal into
`--log_samples` the way 8.2/9.3 assume, so Infrastructure-Failure tagging
can currently only catch an empty response, not an explicit
harness-reported fault (this is exactly what `scripts/robust_run.py`
reconciles against each task's expected item set instead) — this pilot's
empty-response rate turned out to be a genuine, substantial finding in
its own right (`PILOT_RESULTS.md` Section 3), not just a fallback
mechanism.

Corpus/item authoring: `corpus/v0.1/` (2026-09-08) holds the first real
corpus release across all six item families; `corpus/v0.2/` (2026-09-09)
supersedes v0.1's Set B and Set C only — expanded from one fact each to
ten, every fact independently source-verified, and translated into
German, Swahili and Bengali (translations reviewed by the study owner,
2026-09-11); `corpus/v0.3/` (2026-09-15) expands Set A, Set B, Set E and
Set F, directly motivated by the first full pilot run's own findings
(`docs/PILOT_RESULTS.md`) — every new item is `review_status: candidate`,
not yet reviewed by the study owner (see `corpus/v0.3/README.md`'s own
"Review status" section before treating any of it as settled). Each
version's own README states what's verified and what's a scoping choice
rather than an oversight. This folder is under local git
version control (`.gitignore` excludes `results/` at volume) with a clean
working tree, and GitHub/GitLab remotes for public release and backup
(`DATA_MANAGEMENT_PLAN.md` Sections 3, 5, 6). Known open items are
tracked where they arise rather than repeated here: see
`STUDY_PROTOCOL.md` Section 12 (Limitations) and `DATA_MANAGEMENT_PLAN.md`
Section 6 (raw-response backup, once runs exist to back up).
