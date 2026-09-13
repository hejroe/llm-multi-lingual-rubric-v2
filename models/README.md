# models/

GGUF model weights for the `llamacpp` compose service go here. Not tracked
in git (large binaries) — see the project's `.gitignore`.

`docker-compose.yml`'s `llamacpp` service reads `LLAMACPP_MODEL` (default
`model_qwen3_4b.gguf`) to pick which file here to serve, so multiple GGUFs
can live here side by side — switch which one's active with, e.g.:

```bash
LLAMACPP_MODEL=model_qwen3_1.7b.gguf docker compose up -d llamacpp
```

Currently present (both registered Qwen3 candidates, 7.3 — routed through
llama.cpp rather than Ollama for genuine reasoning-mode control, ADR
0010): `model_qwen3_4b.gguf` (obtained by the study owner) and
`model_qwen3_1.7b.gguf` (reused directly from Ollama's own already-
downloaded blob for `qwen3:1.7b` — confirmed a valid GGUF by its magic
bytes, 2026-09-12 — rather than fetching a second copy of the same
weights from elsewhere).

To match a registered candidate (`docs/MODEL_REGISTER.md`) rather than an
arbitrary GGUF, get a GGUF conversion of the same model — e.g. from the
model's own Hugging Face repo if the vendor publishes one, or a
community GGUF conversion (bartowski and unsloth are two commonly-cited
sources, but a conversion is a derivative artefact in its own right and
should be licence-checked the same way the Model Register checks the
original weights, before being treated as equivalent to the registered
model for reportable results).

Placing a model file here (or pointing `LLAMACPP_MODEL` at Ollama's own
already-downloaded blob, as above) is deliberately left to you, the same
way Ollama's own model pulls are (README.md Prerequisites): not something
to bake into the repository or automate.
