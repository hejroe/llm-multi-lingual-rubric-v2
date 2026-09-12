"""Score a whole lm-eval-harness run directory against this project's rubric.

Usage:
    python -m scoring.cli --run-dir results/<output_path>/<model>__<size> \
        --corpus-version v0.2 --out results/scored/<name>.jsonl

Reads every `samples_*.jsonl` in --run-dir (one per task, per
`--log_samples`) plus lm-eval-harness's own aggregated `results_*.json`
(for run-level provenance: model name, backend, timestamp — 9.6), scores
each sample with `scoring.rubric.score_response`, and writes one combined
scored JSONL.

Model digest (5.7/9.6) is auto-detected by default — Ollama's own
`/api/tags` for an `ollama` backend, a computed SHA256 of the GGUF file in
use for a `llamacpp` backend — rather than requiring the operator to run
`ollama list` and copy-paste a value by hand. Pass `--model-digest`
explicitly to override, or `--no-auto-digest` to skip detection entirely.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from scoring.io import (
    RunProvenance,
    auto_detect_model_digest,
    provenance_from_aggregated_results,
    score_jsonl_file,
    write_scored_jsonl,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path, help="e.g. results/verify_corpus_tasks/llama3.2__1b")
    parser.add_argument("--corpus-version", required=True, help="e.g. v0.2 (STUDY_PROTOCOL.md 5.8)")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--model-digest", default=None,
        help="Auto-detected by default (Ollama's own /api/tags for an ollama backend, "
        "a computed SHA256 for a llamacpp/GGUF backend) — pass this only to override.",
    )
    parser.add_argument("--no-auto-digest", action="store_true", help="skip automatic digest detection entirely")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="for automatic digest lookup")
    parser.add_argument("--gguf-path", type=Path, default=None, help="for automatic digest computation (default: models/model.gguf)")
    parser.add_argument(
        "--reasoning-mode", default=None, choices=["enabled", "disabled"],
        help="Qwen3 only (ADR 0010) — which condition this run used; not recoverable from harness output",
    )
    parser.add_argument(
        "--model-name", default=None,
        help="Required only when --run-dir has no results_*.json (scripts/robust_run.py's reconciled "
        "*.missing.jsonl for a run that never produced any real output) — otherwise read from it.",
    )
    parser.add_argument(
        "--backend", default=None,
        help="Required only alongside --model-name, for the same total-failure case.",
    )
    parser.add_argument(
        "--replicate-index", type=int, default=None,
        help="Which of N replications (9.3, scripts/replicate_run.py) this run is — not recoverable from harness output",
    )
    args = parser.parse_args(argv)

    if not args.run_dir.is_dir():
        print(f"error: --run-dir does not exist or is not a directory: {args.run_dir}", file=sys.stderr)
        return 1

    results_jsons = sorted(args.run_dir.glob("results_*.json"))
    sample_files = sorted(args.run_dir.glob("samples_*.jsonl"))

    if not results_jsons:
        # A run that crashed before writing any output at all (scripts/
        # robust_run.py's reconciled *.missing.jsonl is exactly this case)
        # never produces an aggregated results_*.json to build provenance
        # from — found 2026-09-12 trying to score exactly such a file.
        # Fall back to explicit CLI-supplied provenance rather than
        # refusing to score data that exists specifically to record this
        # failure.
        if not sample_files:
            print(f"error: no results_*.json and no samples_*.jsonl found in {args.run_dir} — nothing to score", file=sys.stderr)
            return 1
        if not args.model_name or not args.backend:
            print(
                f"error: no results_*.json found in {args.run_dir} (a total-failure run has no aggregated "
                "results to read provenance from) — pass --model-name and --backend explicitly instead",
                file=sys.stderr,
            )
            return 1
        provenance = RunProvenance(
            corpus_version=args.corpus_version,
            model_name=args.model_name,
            backend=args.backend,
            run_timestamp=datetime.now(tz=timezone.utc).isoformat(),
            model_digest=args.model_digest,
            reasoning_mode=args.reasoning_mode,
            replicate_index=args.replicate_index,
        )
    else:
        if len(results_jsons) > 1:
            print(f"warning: multiple results_*.json found, using the most recent: {results_jsons[-1]}", file=sys.stderr)
        aggregated_results_path = results_jsons[-1]
        provenance = provenance_from_aggregated_results(
            aggregated_results_path,
            corpus_version=args.corpus_version,
            model_digest=args.model_digest,
            reasoning_mode=args.reasoning_mode,
            replicate_index=args.replicate_index,
        )

    if not sample_files:
        print(f"error: no samples_*.jsonl found in {args.run_dir} — was --log_samples passed to lm_eval?", file=sys.stderr)
        return 1

    if provenance.model_digest is None and not args.no_auto_digest:
        detected = auto_detect_model_digest(
            provenance.model_name, provenance.backend, ollama_url=args.ollama_url, gguf_path=args.gguf_path
        )
        if detected:
            provenance.model_digest = detected
            print(f"auto-detected model digest ({provenance.backend}): {detected[:20]}...", file=sys.stderr)
        else:
            print(
                f"note: could not auto-detect a model digest for backend '{provenance.backend}' "
                "(unreachable Ollama / missing GGUF file / unknown backend) — recording none.",
                file=sys.stderr,
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
