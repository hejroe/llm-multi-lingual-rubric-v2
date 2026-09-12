"""Score a whole lm-eval-harness run directory against this project's rubric.

Usage:
    python -m scoring.cli --run-dir results/<output_path>/<model>__<size> \
        --corpus-version v0.2 --out results/scored/<name>.jsonl \
        [--model-digest <digest from `ollama list`>]

Reads every `samples_*.jsonl` in --run-dir (one per task, per
`--log_samples`) plus lm-eval-harness's own aggregated `results_*.json`
(for run-level provenance: model name, backend, timestamp — 9.6), scores
each sample with `scoring.rubric.score_response`, and writes one combined
scored JSONL.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scoring.io import provenance_from_aggregated_results, score_jsonl_file, write_scored_jsonl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path, help="e.g. results/verify_corpus_tasks/llama3.2__1b")
    parser.add_argument("--corpus-version", required=True, help="e.g. v0.2 (STUDY_PROTOCOL.md 5.8)")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--model-digest", default=None, help="from `ollama list` — not recoverable from harness output")
    args = parser.parse_args(argv)

    if not args.run_dir.is_dir():
        print(f"error: --run-dir does not exist or is not a directory: {args.run_dir}", file=sys.stderr)
        return 1

    results_jsons = sorted(args.run_dir.glob("results_*.json"))
    if not results_jsons:
        print(f"error: no results_*.json found in {args.run_dir}", file=sys.stderr)
        return 1
    if len(results_jsons) > 1:
        print(f"warning: multiple results_*.json found, using the most recent: {results_jsons[-1]}", file=sys.stderr)
    aggregated_results_path = results_jsons[-1]

    sample_files = sorted(args.run_dir.glob("samples_*.jsonl"))
    if not sample_files:
        print(f"error: no samples_*.jsonl found in {args.run_dir} — was --log_samples passed to lm_eval?", file=sys.stderr)
        return 1

    provenance = provenance_from_aggregated_results(
        aggregated_results_path, corpus_version=args.corpus_version, model_digest=args.model_digest
    )

    all_results = []
    for sample_file in sample_files:
        print(f"scoring {sample_file.name} ...", file=sys.stderr)
        all_results.extend(score_jsonl_file(sample_file, provenance))

    write_scored_jsonl(all_results, args.out)
    print(f"wrote {len(all_results)} scored rows to {args.out}", file=sys.stderr)

    category_counts: dict[str, int] = {}
    for result in all_results:
        category_counts[result.scored.category.value] = category_counts.get(result.scored.category.value, 0) + 1
    print("category breakdown:", file=sys.stderr)
    for category, count in sorted(category_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {category}: {count}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
