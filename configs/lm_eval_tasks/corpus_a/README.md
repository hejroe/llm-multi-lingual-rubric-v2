# corpus_a Harness Tasks

Closes a gap found during the pilot's first live-model run (2026-09-12,
`docs/adr/0009-custom-corpus-harness-tasks.md`): the stock `mmlu_prox_*`
task runs against the **full upstream MMLU-ProX split** (thousands of
items), not this project's own curated `corpus/vX.Y/set_a.csv` rows, and
carries no field linking a response back to this project's own
`question_id`. These eight tasks read `set_a.csv` directly instead —
`corpus_a_knowledge_{en,de,sw,bn}` (multiple choice, MMLU-ProX-sourced) and
`corpus_a_procedural_{en,de,sw,bn}` (free-text numeric, MGSM-Rev2-sourced),
per Section 5.5's domain split within Set A.

## Usage

```bash
docker compose run --rm eval lm_eval --model local-chat-completions \
  --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
  --apply_chat_template \
  --include_path /configs/lm_eval_tasks \
  --tasks corpus_a_knowledge_en,corpus_a_procedural_en \
  --log_samples --output_path /results/corpus_a_en
```

`--log_samples` is required — this project's own rubric (`scoring/rubric.py`)
scores the raw response text, not lm-eval-harness's own `exact_match`
metric, which is left in place only as a secondary, non-authoritative
sanity signal (its own answer extraction assumes a "the answer is (X)"
convention this project's prompting does not enforce, so expect its
reported accuracy to under-count).

## What's verified, and what isn't

Verified (2026-09-12, against a live `llama3.2:1b` via Ollama): dataset
loads from `corpus/v0.2/set_a.csv` via the `csv` loader with a plain
comma-delimited header row; `process_docs` correctly filters to one
(domain, language) cell per task; `doc.question_id` is preserved in
`--log_samples` output for every row, closing the join-back gap the stock
task had. Not yet verified: Swahili and Bengali specifically (same
mechanism as English/German, expected to behave the same, not
independently re-tested), and the knowledge-domain MCQ prompt against a
model that actually follows a "the answer is (X)" convention.
