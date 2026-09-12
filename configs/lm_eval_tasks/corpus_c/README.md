# corpus_c Harness Tasks

Set C (Temporal-Currency Set, RQ3) had no harness task at all before this
(`docs/adr/0009-custom-corpus-harness-tasks.md`). `corpus_c_{en,de,sw,bn}`
read `corpus/vX.Y/set_c.csv` directly, one task per language, covering
every effective-date version of every fact for that language (filtered
only by language, not by version — RQ3 needs the model queried against
both the stale and current wording, 8.3).

```bash
docker compose run --rm eval lm_eval --model local-chat-completions \
  --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
  --apply_chat_template \
  --include_path /configs/lm_eval_tasks \
  --tasks corpus_c_en --log_samples --output_path /results/corpus_c_en
```

Scored by `scoring/rubric.py`'s Currency-Awareness overlay (8.3), which
needs the sibling version rows for the same underlying fact passed in
alongside each response — see that module's docstring, not lm-eval-
harness's own `exact_match` (left in place only as a non-authoritative
secondary signal).

Verified (2026-09-12): dataset loads and filters correctly by language for
English. Not yet verified: German/Swahili/Bengali specifically, and the
full pipeline against a live model's actual output.
