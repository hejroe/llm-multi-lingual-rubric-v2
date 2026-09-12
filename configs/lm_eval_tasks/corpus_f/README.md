# corpus_f Harness Tasks

Set F (Regional Variety Set, RQ7) had no harness task at all before this
(`docs/adr/0009-custom-corpus-harness-tasks.md`). `corpus_f_uk` and
`corpus_f_au` read `corpus/vX.Y/set_f.csv` directly, filtered by `variety`.
Run alongside `corpus_a_knowledge_en` (the US-English originals, 5.5) — not
a separate "US" variety task here.

```bash
docker compose run --rm eval lm_eval --model local-chat-completions \
  --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
  --apply_chat_template \
  --include_path /configs/lm_eval_tasks \
  --tasks corpus_f_uk,corpus_f_au --log_samples --output_path /results/corpus_f
```

RQ7 (10.3) compares Correct-rate across the US/UK/AU triplet via each row's
`language_variant_of` field, not lm-eval-harness's own `exact_match`. The
matching in `scoring/matching.py` already treats a Set F item's own variety
spelling as equivalent to the US spelling (RUBRIC_CARDS.md's "Correct" card,
common confusion) via `scoring/data/variety_conversion.json`.

Verified (2026-09-12): dataset loads and filters correctly by variety. Not
yet verified: the full pipeline against a live model's actual output.
