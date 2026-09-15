# corpus_e Harness Tasks

Set E (Contamination-Check Set, RQ6) had no harness task at all before this
(`docs/adr/0009-custom-corpus-harness-tasks.md`). `corpus_e_en`/`corpus_e_de`
read `corpus/vX.Y/set_e.csv` directly, filtered by `utils.py`'s
`process_docs`.

English only through corpus-v0.2 (5.5/5.8) — `corpus_e_de` added
corpus-v0.3 (2026-09-15) alongside 5 new German rows in `set_e.csv`,
specifically because RQ6 (10.5) had no primary-language (German)
comparison at all without it. Every new row (both English and German) is
`review_status: candidate`, not `accepted` — 9.4.1 requires mandatory
human review before a candidate is usable, and that review is the study
owner's to give, not this task definition's.

```bash
docker compose run --rm eval lm_eval --model local-chat-completions \
  --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
  --apply_chat_template \
  --include_path /configs/lm_eval_tasks \
  --tasks corpus_e_en,corpus_e_de --log_samples --output_path /results/corpus_e
```

Run alongside `corpus_a_knowledge_en`/`corpus_a_knowledge_de` — RQ6 (10.3)
compares a model's Correct-rate on each Set E item against its own Set A
original via the `language_variant_of` field, not lm-eval-harness's own
`exact_match`.

Verified (2026-09-12): dataset loads correctly. Not yet verified: the full
pipeline against a live model's actual output, for either language.
