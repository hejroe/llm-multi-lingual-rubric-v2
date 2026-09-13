#!/usr/bin/env bash
# Phase 1 of the first full pilot run (STUDY_PROTOCOL.md, 2026-09-12): every
# Ollama-backed registered candidate (7.3) except the two Qwen3 sizes, which
# route through llama.cpp instead for genuine reasoning-mode control (ADR
# 0010, scripts/run_pilot_qwen3_llamacpp.sh) — across the full corpus/v0.2
# (every corpus_* task, ADR 0009), replicated 3 times each (9.3), using
# scripts/replicate_run.py (which wraps scripts/robust_run.py's own
# resilience handling per model).
#
# Run from the docker/ directory in WSL2 (not inside the container) — each
# model runs sequentially, in its own container invocation:
#   bash ../scripts/run_pilot_ollama_models.sh
#
# num_concurrent=1: originally tried at 4 for throughput, but reverted
# (2026-09-13) after a run at that setting coincided with clustered
# Ollama TimeoutErrors and, ultimately, the whole machine becoming
# unresponsive -- plausibly resource contention rather than genuine
# parallelism on this hardware. Slower, but this pilot has hours to run
# regardless, and stability matters more here. Protocol 9.3 already
# treats batched-inference non-determinism as a documented, expected
# variability source (not a methodological violation) that this pilot's
# own 3x replication (9.3) is what actually measures, concurrency level
# included -- so this change doesn't affect what's being tested, only
# how fast it runs.
#
# COOLDOWN_SECONDS between models (2026-09-13): a second incident (machine
# got hot and unresponsive again, this time already at num_concurrent=1)
# suggested sustained back-to-back inference on this laptop's thermal
# envelope -- not concurrency alone -- is a contributing factor. A short
# pause between models gives the chassis a chance to shed heat between
# runs; it does not change what is measured, only adds idle time.

set -euo pipefail

COOLDOWN_SECONDS="${COOLDOWN_SECONDS:-45}"

TASKS="corpus_a_knowledge_en,corpus_a_knowledge_de,corpus_a_knowledge_sw,corpus_a_knowledge_bn,corpus_a_procedural_en,corpus_a_procedural_de,corpus_a_procedural_sw,corpus_a_procedural_bn,corpus_b_en,corpus_b_de,corpus_b_sw,corpus_b_bn,corpus_c_en,corpus_c_de,corpus_c_sw,corpus_c_bn,corpus_e_en,corpus_f_uk,corpus_f_au"

# Parallel arrays (model tags contain ':' themselves, so packing tag+slug
# into one delimited string is error-prone -- kept as two plain arrays
# instead).
MODEL_TAGS=("llama3.2:1b" "smollm2:1.7b" "gemma3n:e2b" "llama3.2:3b" "phi4-mini")
MODEL_SLUGS=("llama3.2_1b" "smollm2_1.7b" "gemma3n_e2b" "llama3.2_3b" "phi4-mini")

for i in "${!MODEL_TAGS[@]}"; do
  model_tag="${MODEL_TAGS[$i]}"
  slug="${MODEL_SLUGS[$i]}"
  echo "=== [$(date '+%H:%M:%S')] Running $model_tag -> /results/pilot/$slug ==="
  docker compose run --rm eval python -m scripts.replicate_run \
    --replications 3 \
    --model local-chat-completions \
    --model_args "base_url=http://host.docker.internal:11434/v1/chat/completions,model=${model_tag},num_concurrent=1,timeout=120,max_retries=2" \
    --apply_chat_template \
    --include_path /configs/lm_eval_tasks \
    --tasks "$TASKS" \
    --output_path "/results/pilot/${slug}"
  echo "=== [$(date '+%H:%M:%S')] Finished $model_tag ==="
  echo "=== Cooling down for ${COOLDOWN_SECONDS}s before next model ==="
  sleep "$COOLDOWN_SECONDS"
done

echo "=== Phase 1 (Ollama-backed models) complete ==="
