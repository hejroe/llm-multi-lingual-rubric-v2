#!/usr/bin/env bash
# Run this INSIDE the container first, before any real evaluation, to confirm
# the container can actually reach your Windows-hosted Ollama server.
#
#   docker compose run --rm eval bash scripts/check_ollama_connectivity.sh
#
# Requires (verified end-to-end 2026-09-12 — see docker-compose.yml's header
# comment for the full explanation of why each piece is needed):
#   1. WSL2 mirrored networking (%USERPROFILE%\.wslconfig: [wsl2]
#      networkingMode=mirrored, then `wsl --shutdown`).
#   2. Ollama bound to all interfaces (OLLAMA_HOST=0.0.0.0), not the
#      127.0.0.1-only default — restart Ollama after setting it.
#   3. A Windows Firewall inbound allow rule for TCP 11434, e.g.:
#      New-NetFirewallRule -DisplayName "Ollama (WSL2)" -Direction Inbound
#        -Protocol TCP -LocalPort 11434 -Action Allow -Profile Any
#   4. This container run with `network_mode: host` (already set in
#      docker-compose.yml) — plain bridge networking cannot reach Windows
#      here even with mirrored networking enabled on the WSL2 side.

set -euo pipefail

echo "Checking http://host.docker.internal:11434/api/tags ..."
if curl -sf --max-time 5 http://host.docker.internal:11434/api/tags; then
  echo
  echo "OK: reached Ollama. The model names above are what you can pass to --model_args model=<name>."
else
  echo
  echo "FAILED: could not reach Ollama at host.docker.internal:11434."
  echo "Things to check (see this script's header comment for the full story):"
  echo "  1. Is Ollama actually running on Windows right now?"
  echo "  2. Is OLLAMA_HOST=0.0.0.0 set and did you restart Ollama after setting it?"
  echo "  3. Does %USERPROFILE%\\.wslconfig have [wsl2] networkingMode=mirrored,"
  echo "     and did you run 'wsl --shutdown' after adding it?"
  echo "  4. Is there a Windows Firewall inbound allow rule for TCP 11434?"
  echo "  5. Is this container actually running with network_mode: host"
  echo "     (docker-compose.yml) rather than plain 'docker run'?"
  exit 1
fi
