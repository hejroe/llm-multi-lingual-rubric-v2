# scripts/

- `check_ollama_connectivity.sh`, `check_llamacpp_connectivity.sh` — run
  before any real evaluation session (README.md's First Run steps 2 and
  5); confirm the eval container can actually reach the backend before
  trusting anything else.
- `robust_run.py` — wraps `lm_eval` itself. Use this instead of calling
  `lm_eval` directly for any real run (STUDY_PROTOCOL.md 9.3's retry
  policy and Infrastructure-Failure handling, 8.2, depend on it). See its
  own module docstring for the full design rationale; in short:

  ```bash
  docker compose run --rm eval python scripts/robust_run.py \
    --model local-chat-completions \
    --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
    --apply_chat_template \
    --include_path /configs/lm_eval_tasks \
    --tasks corpus_b_en,corpus_c_en \
    --output_path /results/corpus_b_and_c_en
  ```

  Applies Protocol 9.3's `timeout=120,max_retries=2` unless the caller's
  own `--model_args` already sets them; retries the whole invocation (up
  to `--run-retries`, default 3) on a crash rather than losing every
  remaining item, using `lm_eval`'s own `--use_cache` so completed items
  are never redundantly re-queried; and reconciles the final output
  against each task's full expected item set (respecting `--limit`),
  writing anything that never got a response as an explicit
  `*.missing.jsonl` — `scoring.cli` picks these up the same way as any
  other samples file, and they'll score as Infrastructure-Failure (an
  empty response) with no further changes needed.

  Verified live (2026-09-12) against both a real transient-style run and
  a deliberate total-connection-failure case (see the commit history for
  the two bugs that first pass of testing actually caught: unlimited
  `--limit` runs wrongly flagging every un-run item as missing, and a
  crash so early that no output directory existed at all being wrongly
  reported as "recovered"). Not yet run against a genuinely intermittent
  failure (some items succeed, one specific item times out) — every test
  so far has been either "every item succeeds" or "every item fails",
  since that's what's straightforward to induce deliberately; the
  reconciliation logic doesn't distinguish between those cases and should
  behave the same either way, but hasn't been independently exercised
  against a real intermittent failure.

  Runs INSIDE the eval container (it needs `lm_eval` and `datasets`,
  already installed there) — not part of the local `scoring`/`analysis`
  Python environment (`requirements.txt`), which stays lightweight
  deliberately.

- `replicate_run.py` — wraps `robust_run.py` to run the same task(s) N
  times (STUDY_PROTOCOL.md 9.3's replication; 3 is this pilot's own
  starting value, not a ceiling on N — ADR 0003). Any replication count is
  supported, e.g. `--replications 100` for someone demonstrating answer
  stability for their own fine-tuned model against their own rubric:

  Invoke as a module (`-m scripts.replicate_run`), not a direct file path
  — it imports `scripts.robust_run`, and `python scripts/replicate_run.py`
  puts only the script's own directory on `sys.path`, not the repo root,
  so that import fails (found 2026-09-12, running it live for the first
  time — `robust_run.py` itself has no such cross-import and is fine
  invoked either way):

  ```bash
  docker compose run --rm eval python -m scripts.replicate_run \
    --replications 100 \
    --model local-chat-completions \
    --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
    --apply_chat_template \
    --include_path /configs/lm_eval_tasks \
    --tasks corpus_b_en \
    --output_path /results/corpus_b_en_stability
  ```

  Writes `<output_path>/replicate_000/`, `replicate_001/`, ... — score
  each directory separately with `scoring.cli` (passing
  `--replicate-index <i>`), then concatenate the scored JSONLs before
  `analysis.reliability.compute_reliability`, which needs no special
  handling for the replication count: rows sharing the same (model_name,
  question_id) key are the replicates, however many there are. Each
  replicate is a fully independent re-query (own `--use_cache`, own
  output directory) with the *same* seed as every other run in this
  project, deliberately — see the module's own docstring for why.

- `run_pilot_ollama_models.sh` — Phase 1 of the first full pilot run: every
  Ollama-backed registered candidate (7.3) except the two Qwen3 sizes,
  across the full corpus (every `corpus_*` task, ADR 0009), replicated 3
  times each (9.3), via `replicate_run.py`. Run from the `docker/`
  directory in WSL2, **not** inside the container (it invokes `docker
  compose run` itself once per model):

  ```bash
  cd docker
  bash ../scripts/run_pilot_ollama_models.sh
  ```

  Sequential by design — one model at a time, `num_concurrent=1` — after
  a real incident (2026-09-13) where higher concurrency coincided with
  the whole machine becoming unresponsive, plausibly resource contention
  rather than genuine parallelism on modest hardware. A `COOLDOWN_SECONDS`
  pause (default 45, override via env var) runs between models for the
  same reason. None of this changes what's being measured — Protocol 9.3
  already treats batched-inference non-determinism, concurrency included,
  as a documented variability source that the pilot's own 3x replication
  measures, not a methodological violation.

- `run_pilot_qwen3_llamacpp.sh` — Phase 2: both registered Qwen3 sizes,
  routed through llama.cpp instead of Ollama specifically so reasoning
  mode can be controlled (ADR 0010) — Ollama's OpenAI-compatible endpoint
  was confirmed (2026-09-12) to ignore the `think` parameter entirely.
  Run the same way as Phase 1, after it completes (both scripts want the
  GPU). Switches the `llamacpp` compose service between the two GGUF
  sizes itself (`models/README.md`) and waits for its health check before
  each condition:

  ```bash
  cd docker
  bash ../scripts/run_pilot_qwen3_llamacpp.sh
  ```

  Each size runs both conditions (reasoning enabled/disabled) via
  llama.cpp's `chat_template_kwargs: {enable_thinking: ...}` — the
  mechanism that actually works, unlike Ollama's `think` parameter above
  — 3 replicates each, same as Phase 1.

- `monitor_thermals.ps1` — optional background watchdog for either phase
  above: logs CPU%, free RAM, and GPU temp/utilization/power draw every
  30s to `results/thermal_log.csv`. Read-only, takes no action on the
  system. Run from an ordinary PowerShell window left open for the
  pilot's duration:

  ```powershell
  powershell -File scripts\monitor_thermals.ps1
  ```

  Written after a real incident where request-timing became erratic
  shortly before the machine became unresponsive; the log gives a
  timestamped record to diagnose against if it happens again, instead of
  a single post-hoc snapshot.

Once Phase 1 (and Phase 2, if running Qwen3) complete, see
`scoring/score_pilot_run.py` (module docstring) to score every run in one
pass rather than calling `scoring.cli` once per model/replicate/condition
by hand.
