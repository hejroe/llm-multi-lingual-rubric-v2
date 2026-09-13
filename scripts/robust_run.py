#!/usr/bin/env python3
"""Wrapper around `lm_eval` that closes the Infrastructure-Failure gap
`scoring/io.py`'s module docstring describes: stock lm-eval-harness's
per-request retry either succeeds silently or, once exhausted, raises an
exception that crashes the *entire* run -- it never surfaces a per-item
failure signal the way STUDY_PROTOCOL.md 8.2/9.3 assume.

Investigated 2026-09-12 (lm_eval/models/api_models.py): `max_retries`
(default 3) and `timeout` (default 300s) are real, configurable
`model_args`, but nothing in this project's documented commands actually
set them -- meaning every run so far silently used the harness's own
defaults, not Protocol 9.3's stated 120s timeout / one-retry policy. This
script applies those defaults unless the caller overrides them.

For the crash case itself: reimplementing lm-eval-harness's internal
retry-then-reraise logic (api_models.py's generate_until) was considered
and rejected as too fragile -- it would couple this project to private
implementation details likely to change on any upstream version bump,
undermining the very reproducibility ADR-adjacent pinning (Dockerfile)
just fixed. Instead: retry the *whole* `lm_eval` invocation on a crash,
using its own `--use_cache` flag (a real, documented, public CLI option)
so already-completed items are never redundantly re-queried -- and, once
retries are exhausted, reconcile the actual output against the task's own
full expected item set (rebuilt the same way the harness itself would,
via its own `_yaml_loader` and `datasets.load_dataset`) so anything that
still never got a response is made explicit rather than silently missing.
Never mutates the harness's own raw samples file (Protocol 5.7) -- missing
items are written to a separate `*.missing.jsonl` alongside it, which
`scoring.cli` picks up the same way as any other samples file.

Usage (run INSIDE the eval container, in place of calling `lm_eval`
directly):

    python scripts/robust_run.py \
      --model local-chat-completions \
      --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,\
model=llama3.2:1b,num_concurrent=1 \
      --apply_chat_template \
      --include_path /configs/lm_eval_tasks \
      --tasks corpus_b_en,corpus_c_en \
      --output_path /results/corpus_b_and_c_en \
      [--limit 5] [--run-retries 3]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMEOUT = 120  # Protocol 9.3
DEFAULT_MAX_RETRIES = 2  # Protocol 9.3: "one retry on timeout" = 2 total attempts


def ensure_resilience_args(model_args: str) -> str:
    """Inject timeout/max_retries into a model_args string if the caller
    hasn't already set them, so Protocol 9.3's stated values are what
    actually get used rather than the harness's own (undocumented, in
    this project's context) defaults."""
    parts = [p for p in model_args.split(",") if p]
    keys = {p.split("=", 1)[0] for p in parts}
    if "timeout" not in keys:
        parts.append(f"timeout={DEFAULT_TIMEOUT}")
    if "max_retries" not in keys:
        parts.append(f"max_retries={DEFAULT_MAX_RETRIES}")
    return ",".join(parts)


def build_lm_eval_args(args: argparse.Namespace) -> list[str]:
    lm_eval_args = [
        "--model",
        args.model,
        "--model_args",
        ensure_resilience_args(args.model_args),
        "--tasks",
        args.tasks,
        "--include_path",
        args.include_path,
        "--output_path",
        args.output_path,
        "--log_samples",
        # Plain string join, not pathlib: this script only ever runs
        # inside the (Linux) eval container, and args.output_path is
        # always a POSIX path there (e.g. /results/...) regardless of
        # what platform a caller's own Python interpreter happens to be —
        # pathlib.Path would use the *interpreter's* OS separator instead.
        "--use_cache",
        args.output_path.rstrip("/") + "/.cache",
    ]
    if args.apply_chat_template:
        lm_eval_args.append("--apply_chat_template")
    if args.limit is not None:
        lm_eval_args.extend(["--limit", str(args.limit)])
    if args.gen_kwargs is not None:
        lm_eval_args.extend(["--gen_kwargs", args.gen_kwargs])
    return lm_eval_args


def run_with_recovery(lm_eval_args: list[str], run_retries: int) -> int:
    """Re-invoke the same lm_eval command up to `run_retries` times if it
    crashes. --use_cache means already-completed items are skipped on a
    retry, not redundantly re-queried."""
    last_returncode = 1
    for attempt in range(1, run_retries + 1):
        print(
            f"[robust_run] attempt {attempt}/{run_retries}: "
            f"lm_eval {' '.join(lm_eval_args)}",
            file=sys.stderr,
        )
        result = subprocess.run(["lm_eval", *lm_eval_args])
        last_returncode = result.returncode
        if last_returncode == 0:
            return 0
        print(
            f"[robust_run] attempt {attempt} exited with code {last_returncode}",
            file=sys.stderr,
        )
    print(
        f"[robust_run] WARNING: did not complete cleanly after {run_retries} attempts. "
        "Reconciling against each task's expected item set now.",
        file=sys.stderr,
    )
    return last_returncode


def model_output_subdir(output_path: Path, model_args: str) -> Path:
    """The exact per-model subdirectory lm-eval-harness itself writes
    results under (`<output_path>/<sanitized model name>/`) — computed
    directly via the harness's own `sanitize_model_name` (lm_eval/utils.py)
    from the `model=` key in `--model_args`, rather than discovered by
    globbing for whatever happens to already exist. Globbing fails exactly
    in the case reconciliation matters most: a crash so early that the
    harness never created the directory or wrote anything into it at all —
    that must still reconcile as "every item missing", not be skipped."""
    from lm_eval.utils import sanitize_model_name

    model_name = "unknown"
    for part in model_args.split(","):
        if part.startswith("model="):
            model_name = part.split("=", 1)[1]
            break
    return output_path / sanitize_model_name(model_name)


def _load_task_dataset(task_yaml_path: Path, limit: float | None):
    """Rebuild a task's exact expected doc set the same way the harness
    itself would, using its own (public) yaml loader and dataset loading —
    not a hand-maintained parallel mapping that could drift out of sync.
    Applies `--limit` the same way lm_eval/api/task.py does
    (`instances[:og_limit]`, a plain slice of doc order) — otherwise a
    smoke-test run with --limit would have every item beyond the limit
    wrongly reconciled as a missing/failed response, when they were simply
    never scheduled to run at all (found via a deliberate --limit 2 test,
    2026-09-12: 28 of 30 Set B English rows were wrongly flagged missing)."""
    from datasets import load_dataset
    from lm_eval.tasks._yaml_loader import load_yaml

    cfg = load_yaml(task_yaml_path)
    dataset = load_dataset(
        cfg["dataset_path"],
        data_files=cfg["dataset_kwargs"]["data_files"],
        split=cfg["test_split"],
    )
    if cfg.get("process_docs"):
        dataset = cfg["process_docs"](dataset)
    if limit is not None:
        dataset = dataset.select(range(min(int(limit), len(dataset))))
    return dataset


def reconcile_task(
    task_name: str, include_path: Path, model_output_dir: Path, limit: float | None
) -> int:
    """Compare a task's actual samples_*.jsonl against its full expected
    doc set; write any missing question_ids as empty-response stub rows
    to a separate *.missing.jsonl (scoring/rubric.py already tags an empty
    response Infrastructure-Failure — no separate marker needed). Returns
    the count reconciled. `model_output_dir` need not already exist (a
    crash before the harness wrote anything at all is exactly the case
    this needs to handle correctly)."""
    task_yaml_candidates = list(include_path.glob(f"*/{task_name}.yaml"))
    if not task_yaml_candidates:
        print(
            f"[robust_run] reconcile: no YAML found for task '{task_name}', skipping",
            file=sys.stderr,
        )
        return 0
    task_yaml_path = task_yaml_candidates[0]

    sample_files = (
        sorted(model_output_dir.glob(f"samples_{task_name}_*.jsonl"))
        if model_output_dir.is_dir()
        else []
    )
    actual_ids: set[str] = set()
    if sample_files:
        samples_path = sample_files[-1]
        with open(samples_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    actual_ids.add(json.loads(line)["doc"]["question_id"])
    else:
        print(
            f"[robust_run] reconcile: no samples file at all for "
            f"'{task_name}' — every item is missing",
            file=sys.stderr,
        )
        model_output_dir.mkdir(parents=True, exist_ok=True)
        samples_path = model_output_dir / f"samples_{task_name}_norun.jsonl"

    dataset = _load_task_dataset(task_yaml_path, limit)
    docs_by_id = {row["question_id"]: dict(row) for row in dataset}
    missing_ids = set(docs_by_id) - actual_ids
    if not missing_ids:
        return 0

    missing_path = samples_path.parent / (samples_path.stem + ".missing.jsonl")
    with open(missing_path, "w", encoding="utf-8") as f:
        for qid in sorted(missing_ids):
            f.write(
                json.dumps(
                    {
                        "doc": docs_by_id[qid],
                        "resps": [[]],
                        "filtered_resps": ["[no_response]"],
                    }
                )
                + "\n"
            )

    print(
        f"[robust_run] reconcile: '{task_name}': {len(missing_ids)} item(s) "
        f"never got a response -> {missing_path}",
        file=sys.stderr,
    )
    return len(missing_ids)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--model", default="local-chat-completions")
    parser.add_argument("--model_args", required=True)
    parser.add_argument("--tasks", required=True, help="comma-separated task names")
    parser.add_argument("--include_path", required=True)
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--apply_chat_template", action="store_true")
    parser.add_argument("--limit", type=float, default=None)
    parser.add_argument(
        "--gen_kwargs",
        default=None,
        help=(
            "passed through verbatim to lm_eval's own --gen_kwargs (e.g. "
            "Qwen3's llama.cpp reasoning-mode toggle, ADR 0010: a JSON "
            "object like {chat_template_kwargs: {enable_thinking: false}}). "
            "Found 2026-09-13: this script's argparse had no such option, "
            "so scripts/run_pilot_qwen3_llamacpp.sh's non-reasoning "
            "condition (the primary, pre-registered one, ADR 0010) crashed "
            "with 'unrecognized arguments' before lm_eval was ever invoked "
            "-- silently, since the reasoning condition (no --gen_kwargs) "
            "succeeded and made the failure easy to miss on partial testing."
        ),
    )
    parser.add_argument(
        "--run-retries", type=int, default=3, help="whole-invocation retries on crash"
    )
    args = parser.parse_args(argv)

    lm_eval_args = build_lm_eval_args(args)
    returncode = run_with_recovery(lm_eval_args, args.run_retries)

    model_output_dir = model_output_subdir(Path(args.output_path), args.model_args)
    total_missing = 0
    for task_name in args.tasks.split(","):
        total_missing += reconcile_task(
            task_name.strip(), Path(args.include_path), model_output_dir, args.limit
        )

    if returncode != 0:
        if total_missing == 0:
            print(
                "[robust_run] run did not exit cleanly, but reconciliation "
                "found no missing items — treating as recovered.",
                file=sys.stderr,
            )
        else:
            print(
                f"[robust_run] run did not complete cleanly; "
                f"{total_missing} item(s) reconciled as "
                "Infrastructure-Failure.",
                file=sys.stderr,
            )
    elif total_missing:
        print(
            f"[robust_run] {total_missing} item(s) total reconciled as "
            "Infrastructure-Failure across all tasks.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
