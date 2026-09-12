# corpus_e Harness Task

Set E (Contamination-Check Set, RQ6) had no harness task at all before this
(`docs/adr/0009-custom-corpus-harness-tasks.md`). `corpus_e_en` reads
`corpus/vX.Y/set_e.csv` directly. English only at this corpus version
(5.5/5.8) — no `process_docs` filter needed.

```bash
docker compose run --rm eval lm_eval --model local-chat-completions \
  --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
  --apply_chat_template \
  --include_path /configs/lm_eval_tasks \
  --tasks corpus_e_en --log_samples --output_path /results/corpus_e_en
```

Run alongside `corpus_a_knowledge_en` — RQ6 (10.3) compares a model's
Correct-rate on each Set E item against its own Set A original via the
`language_variant_of` field, not lm-eval-harness's own `exact_match`.

Verified (2026-09-12): dataset loads correctly. Not yet verified: the full
pipeline against a live model's actual output.
