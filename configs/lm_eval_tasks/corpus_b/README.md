# corpus_b Harness Tasks

Set B (Jurisdiction-Contingent Set, RQ2) had no harness task at all before
this (`docs/adr/0009-custom-corpus-harness-tasks.md`) — a hand-authored
corpus with no stock benchmark equivalent. `corpus_b_{en,de,sw,bn}` read
`corpus/vX.Y/set_b.csv` directly, one task per language, covering every
jurisdiction/unspecified variant for that language.

```bash
docker compose run --rm eval lm_eval --model local-chat-completions \
  --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
  --apply_chat_template \
  --include_path /configs/lm_eval_tasks \
  --tasks corpus_b_en --log_samples --output_path /results/corpus_b_en
```

Scored by `scoring/rubric.py`'s Jurisdiction-Adaptation overlay (8.3), which
needs the *sibling* rows for the same underlying fact (the other
jurisdiction/unspecified variants) passed in alongside each response — see
that module's docstring, not lm-eval-harness's own `exact_match` (left in
place only as a non-authoritative secondary signal; the unspecified variant
in particular carries no `gold_answer` at all, 5.5).

Verified (2026-09-12): dataset loads and filters correctly by language for
English. Not yet verified: German/Swahili/Bengali specifically (same
mechanism, not independently re-tested), and the full pipeline against a
live model's actual output.
