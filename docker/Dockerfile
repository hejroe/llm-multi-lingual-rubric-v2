# Dockerfile for the redesigned multilingual LLM evaluation pilot.
#
# Runs lm-evaluation-harness (https://github.com/EleutherAI/lm-evaluation-harness)
# against locally-hosted models via Ollama's OpenAI-compatible API. This container
# only needs network access to your Ollama server (via host.docker.internal) and,
# on first run, to HuggingFace to download the MGSM / MMLU-ProX / AfriMGSM dataset
# files - it does not run any models itself.
#
# Build (from the docker/ directory, or with -f docker/Dockerfile from the repo root):
#   docker build -t llm-eval-pilot -f docker/Dockerfile .
#
# Example smoke-test run (adjust model name to one you have pulled in Ollama).
# --add-host is required because we're using native Docker Engine (not Docker
# Desktop), which does not map host.docker.internal automatically:
#   docker run --rm \
#     --add-host=host.docker.internal:host-gateway \
#     -v "$(pwd)/results:/results" \
#     -v "$(pwd)/configs:/configs" \
#     llm-eval-pilot \
#     lm_eval --model local-chat-completions \
#       --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3:8b,num_concurrent=1 \
#       --tasks mgsm_direct_de \
#       --limit 5 \
#       --output_path /results/smoke_test_mgsm_de

# Pinned by digest (2026-09-12), not a floating tag -- Protocol 9.7 says every
# run's stack should be reproducible from its version numbers alone; a bare
# `python:3.11-slim` tag can silently point at a different image on a later
# rebuild, which contradicts that. Re-resolve with `docker pull python:3.11-slim`
# + `docker inspect ... --format '{{index .RepoDigests 0}}'` if this ever needs
# bumping deliberately.
FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534

# git is needed to install lm-eval-harness directly from GitHub (rather than a
# possibly-stale PyPI release), so we get the mgsm / mmlu_prox / afrimgsm task
# definitions and the local-chat-completions model type confirmed present.
RUN apt-get update && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

# Upgrading pip/setuptools/wheel first avoids a build failure seen with some of
# lm-eval-harness's older transitive dependencies (rouge-score, word2number)
# under newer setuptools defaults.
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install lm-evaluation-harness with the "api" extra (needed for the
# local-completions / local-chat-completions model types that talk to an
# OpenAI-compatible server such as Ollama). Pinned to a specific commit
# (2026-09-12), not the floating main branch, for the same reproducibility
# reason as the base image above -- this had been an unpinned `git+...`
# reference since this project's first build, which a rebuild today would
# have silently resolved to a different, later commit than every run so far
# was actually verified against. The exact commit originally installed isn't
# recoverable after the fact (pip discards a git checkout's history once it
# builds the wheel, and no run this project has done so far recorded it) --
# this pin is a forward-looking fix from today's HEAD, not a retroactive one.
RUN pip install --no-cache-dir "lm-eval[api] @ git+https://github.com/EleutherAI/lm-evaluation-harness.git@ad8737ae7fad24cf64e50fc7fc31397bff586b9e"

# Non-root user for defense in depth - this container has no reason to run as root.
RUN useradd --create-home --shell /bin/bash runner
USER runner
WORKDIR /home/runner

ENTRYPOINT []
CMD ["bash"]
