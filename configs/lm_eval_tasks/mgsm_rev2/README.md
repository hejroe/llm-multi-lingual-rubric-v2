# Custom MGSM-Rev2 Harness Tasks

Closes the gap tracked in `docs/STUDY_PROTOCOL.md` Section 12.8 and
`docs/adr/0008-mgsm-rev2-custom-task.md`: the stock lm-evaluation-harness
`mgsm` task loads the original, excluded MGSM dataset. These four task
definitions load the vetted MGSM-Rev2 replacement instead, for the
Protocol's candidate languages (German, Swahili, Bengali, plus English as
Set A/F's source language).

## Usage

Mount this whole `lm_eval_tasks/` directory into the harness container
(already done via `docker-compose.yml`'s existing `../configs:/configs`
volume — just place this folder at `configs/lm_eval_tasks/`), then pass
`--include_path /configs/lm_eval_tasks` to `lm_eval`:

```bash
docker compose run --rm eval lm_eval --model local-chat-completions \
  --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
  --include_path /configs/lm_eval_tasks \
  --tasks mgsm_rev2_direct_de \
  --limit 5 \
  --output_path /results/smoke_test_mgsm_rev2_de
```

## What's verified, and what isn't

Verified directly (2026-09-08, against a real lm-evaluation-harness
install, not assumed): the dataset loads correctly from the vendored TSVs
via the `csv` loader with `column_names`/`delimiter` overrides; all 250
rows per language load; `doc_to_text`/`doc_to_target` render correctly for
German and Bengali (confirming both Latin and non-Latin script handling);
a `generate_until` request constructs without error.

Not yet verified: the full filter/scoring pipeline against a real model's
output (needs a live backend — the pilot's first real run, not this
scaffolding step), and Swahili/English specifically (same TSV format and
mechanism as the two verified languages, so expected to behave the same,
but not independently re-tested here).

## Task/prompt conventions

Deliberately mirrors the stock `mgsm_direct_*` tasks' exact prompt
conventions per language (including where the original only localises the
question-cue word and leaves "Answer:" in English for Swahili and
Bengali) — this is a faithful drop-in replacement for the dataset only,
not a redesign of the prompting method, so results stay comparable in
method to the wider MGSM literature.
