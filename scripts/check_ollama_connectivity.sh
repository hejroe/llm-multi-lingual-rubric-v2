#!/usr/bin/env bash
# Run this INSIDE the container first, before any real evaluation, to confirm
# the container can actually reach your Windows-hosted Ollama server through
# WSL2's localhost forwarding.
#
#   docker run --rm --add-host=host.docker.internal:host-gateway llm-eval-pilot \
#     bash /home/runner/scripts/check_ollama_connectivity.sh
#
# (or, if using docker compose: docker compose run --rm eval bash scripts/check_ollama_connectivity.sh)

set -euo pipefail

echo "Checking http://host.docker.internal:11434/api/tags ..."
if curl -sf --max-time 5 http://host.docker.internal:11434/api/tags; then
  echo
  echo "OK: reached Ollama. The model names above are what you can pass to --model_args model=<name>."
else
  echo
  echo "FAILED: could not reach Ollama at host.docker.internal:11434."
  echo "Things to check:"
  echo "  1. Is Ollama actually running on Windows right now?"
  echo "  2. Did you pass --add-host=host.docker.internal:host-gateway to 'docker run'?"
  echo "  3. Is Ollama bound to 0.0.0.0 rather than only 127.0.0.1? (OLLAMA_HOST=0.0.0.0 may be needed)"
  echo "  4. Does Windows Firewall allow the connection from WSL2?"
  exit 1
fi
