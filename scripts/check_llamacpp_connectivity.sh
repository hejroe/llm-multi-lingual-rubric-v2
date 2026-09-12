#!/usr/bin/env bash
# Run this INSIDE the eval container first, before any Set D (RQ4) run, to
# confirm it can reach the containerised llama.cpp server.
#
#   docker compose run --rm eval bash scripts/check_llamacpp_connectivity.sh
#
# Requires the llamacpp service to already be running:
#   docker compose up -d llamacpp
#
# Reached via its published port (http://localhost:8081), not compose
# service-name DNS (http://llamacpp:8080) — the `eval` service now runs with
# `network_mode: host` (docker-compose.yml, needed for the Ollama path, see
# its header comment), which bypasses the compose bridge network's DNS
# entirely. localhost:8081 works because eval shares the WSL2 host's network
# namespace, where llamacpp's port is published.

set -euo pipefail

echo "Checking http://localhost:8081/health ..."
if curl -sf --max-time 5 http://localhost:8081/health; then
  echo
  echo "OK: llama.cpp server is reachable and healthy."
  echo "Checking /v1/models for the loaded model name..."
  curl -sf --max-time 5 http://localhost:8081/v1/models
  echo
else
  echo
  echo "FAILED: could not reach llama.cpp at localhost:8081."
  echo "Things to check:"
  echo "  1. Is the llamacpp service actually started? (docker compose up -d llamacpp)"
  echo "  2. Does ../models/model.gguf exist? (see models/README.md)"
  echo "  3. Does 'docker compose logs llamacpp' show a GPU/CUDA error? Confirm"
  echo "     the NVIDIA Container Toolkit is installed and 'docker run --rm"
  echo "     --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi' works."
  echo "  4. Are you trying to run this at the same time as an Ollama-serving"
  echo "     run? Both want the GPU — stop one before starting the other"
  echo "     (docs/STUDY_PROTOCOL.md 9.2)."
  exit 1
fi
