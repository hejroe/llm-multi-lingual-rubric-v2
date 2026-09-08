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

FROM python:3.11-slim

# git is needed to install lm-eval-harness directly from GitHub (rather than a
# possibly-stale PyPI release), so we get the mgsm / mmlu_prox / afrimgsm task
# definitions and the local-chat-completions model type confirmed present on
# the main branch during this project's review.
RUN apt-get update && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

# Upgrading pip/setuptools/wheel first avoids a build failure seen with some of
# lm-eval-harness's older transitive dependencies (rouge-score, word2number)
# under newer setuptools defaults.
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install lm-evaluation-harness with the "api" extra (needed for the
# local-completions / local-chat-completions model types that talk to an
# OpenAI-compatible server such as Ollama).
RUN pip install --no-cache-dir "lm-eval[api] @ git+https://github.com/EleutherAI/lm-evaluation-harness.git"

# Non-root user for defense in depth - this container has no reason to run as root.
RUN useradd --create-home --shell /bin/bash runner
USER runner
WORKDIR /home/runner

ENTRYPOINT []
CMD ["bash"]
