# models/

GGUF model weights for the `llamacpp` compose service go here. Not tracked
in git (large binaries) — see the project's `.gitignore`.

Place exactly one file named `model.gguf` here to match
`docker-compose.yml`'s `-m /models/model.gguf`, or edit that path if you'd
rather keep the original filename and swap models by relinking.

To match a registered candidate (`docs/MODEL_REGISTER.md`) rather than an
arbitrary GGUF, get a GGUF conversion of the same model — e.g. from the
model's own Hugging Face repo if the vendor publishes one, or a
community GGUF conversion (bartowski and unsloth are two commonly-cited
sources, but a conversion is a derivative artefact in its own right and
should be licence-checked the same way the Model Register checks the
original weights, before being treated as equivalent to the registered
model for reportable results).

This step — actually placing a model file here — is deliberately left to
you, the same way Ollama's own model pulls are (README.md Prerequisites):
not something to bake into the repository or automate silently.
