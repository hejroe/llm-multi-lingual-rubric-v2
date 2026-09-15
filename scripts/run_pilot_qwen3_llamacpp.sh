#!/usr/bin/env bash
# Phase 2 of the first full pilot run (STUDY_PROTOCOL.md, 2026-09-12): both
# registered Qwen3 sizes (7.3), routed through llama.cpp instead of Ollama
# specifically so reasoning mode can actually be controlled (ADR 0010) --
# Ollama's OpenAI-compatible endpoint was confirmed (2026-09-12) to ignore
# the `think` parameter entirely, unlike llama.cpp's own endpoint, which
# respects `chat_template_kwargs: {enable_thinking: false/true}` correctly
# (verified live against both raw HTTP and the harness's own --gen_kwargs).
#
# Each Qwen3 size runs in BOTH conditions -- non-reasoning (primary,
# pre-registered, per ADR 0010) and reasoning (secondary, descriptive) --
# each its own replicate_run.py invocation (3 replications, 9.3), across
# the full corpus, the same as Phase 1.
#
# Run from the docker/ directory in WSL2 (not inside the container). Stop
# any Phase 1 (Ollama) run before starting this -- both want the GPU
# (Protocol 9.2, 8GB VRAM) -- though Ollama's own model only occupies VRAM
# while actively serving a request, so brief overlap at a phase boundary
# is unlikely to matter in practice; avoid running them concurrently on
# purpose regardless.
#   bash ../scripts/run_pilot_qwen3_llamacpp.sh

set -euo pipefail

TASKS="corpus_a_knowledge_en,corpus_a_knowledge_de,corpus_a_knowledge_sw,corpus_a_knowledge_bn,corpus_a_procedural_en,corpus_a_procedural_de,corpus_a_procedural_sw,corpus_a_procedural_bn,corpus_b_en,corpus_b_de,corpus_b_sw,corpus_b_bn,corpus_c_en,corpus_c_de,corpus_c_sw,corpus_c_bn,corpus_e_en,corpus_e_de,corpus_f_uk,corpus_f_au"

wait_for_llamacpp() {
  echo "Waiting for llama.cpp to report healthy..."
  for _ in $(seq 1 60); do
    if curl -sf --max-time 3 http://localhost:8081/health >/dev/null 2>&1; then
      echo "llama.cpp is healthy."
      return 0
    fi
    sleep 5
  done
  echo "ERROR: llama.cpp did not become healthy within 5 minutes." >&2
  return 1
}

run_condition() {
  local slug="$1"
  local gen_kwargs_json="$2"  # empty string = reasoning enabled (default)
  local extra_args=()
  if [ -n "$gen_kwargs_json" ]; then
    extra_args=(--gen_kwargs "$gen_kwargs_json")
  fi
  echo "=== [$(date '+%H:%M:%S')] Running $slug -> /results/pilot/$slug ==="
  docker compose run --rm eval python -m scripts.replicate_run \
    --replications 3 \
    --model local-chat-completions \
    --model_args "base_url=http://localhost:8081/v1/chat/completions,model=llamacpp,num_concurrent=1,timeout=120,max_retries=2" \
    --apply_chat_template \
    "${extra_args[@]}" \
    --include_path /configs/lm_eval_tasks \
    --tasks "$TASKS" \
    --output_path "/results/pilot/${slug}"
  echo "=== [$(date '+%H:%M:%S')] Finished $slug ==="
}

# --- Qwen3 1.7B ---
echo "--- Switching llama.cpp to Qwen3 1.7B ---"
LLAMACPP_MODEL=model_qwen3_1.7b.gguf docker compose up -d llamacpp
wait_for_llamacpp
run_condition "qwen3_1.7b_nonreasoning" '{"chat_template_kwargs": {"enable_thinking": false}}'
run_condition "qwen3_1.7b_reasoning" ""

# --- Qwen3 4B ---
echo "--- Switching llama.cpp to Qwen3 4B ---"
LLAMACPP_MODEL=model_qwen3_4b.gguf docker compose up -d llamacpp
wait_for_llamacpp
run_condition "qwen3_4b_nonreasoning" '{"chat_template_kwargs": {"enable_thinking": false}}'
run_condition "qwen3_4b_reasoning" ""

echo "=== Phase 2 (Qwen3 via llama.cpp, both sizes, both conditions) complete ==="
