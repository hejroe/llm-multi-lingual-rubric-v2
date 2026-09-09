# 0001. Inference backend abstraction, with Ollama as default

**Status:** Accepted
**Date:** 2026-09-08

## Context

The study needs to run open-weight models locally, reproducibly, and
across multiple model families (7). Ollama is the most widely deployed
local runner among informal, casual deployments — relevant because 7.1's
model-selection rationale concerns real-world casual deployment risk, not
only multilingual-specialist use. Its OpenAI-compatible endpoint, however,
omits `tool-choice`, `logprobs`, and `logit-bias`, per its own
compatibility documentation. llama.cpp's `llama-server` and vLLM both
expose a more complete OpenAI-compatible surface, including tool-calling
parameters. LM Studio was excluded as GUI-only, incompatible with
unattended, container-based runs.

## Decision

Use `lm-evaluation-harness`'s `local-chat-completions` model type as the
harness-level abstraction across all backends (9.2). Ollama is the default
backend for Sets A, B, C, E, and F. Set D (RQ4, tool-calling) is routed to
llama.cpp or vLLM specifically, because Ollama's compat layer cannot
exercise the parameters RQ4 needs to test.

## Consequences

Set D results are not directly comparable to same-model results run under
Ollama for the other sets, since the backend itself differs — this is
stated as a limitation (12), not absorbed silently into the results.
Adding a new backend later only requires it to speak the OpenAI-compatible
chat-completions schema; no other part of the pipeline is backend-specific.
