"""Score every run in the first full pilot (STUDY_PROTOCOL.md, 2026-09-12)
in one pass: walks `results/pilot/<slug>/replicate_NNN/<sanitized-model>/`,
infers each run's provenance from its own directory name (reasoning_mode
from a `_reasoning`/`_nonreasoning` slug suffix, replicate_index from
`replicate_NNN`) rather than requiring 27 separate `scoring.cli` calls with
manually-typed flags, and writes one combined scored JSONL.

Usage (plain local Python, from the repo root — no Docker/WSL needed, same
as scoring.cli and analysis.cli):
    python -m scoring.score_pilot_run --pilot-root results/pilot \
        --out results/scored/pilot_all.jsonl
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from scoring.io import (
    RunProvenance,
    auto_detect_model_digest,
    provenance_from_aggregated_results,
    score_jsonl_file,
    write_scored_jsonl,
)

_REPLICATE_RE = re.compile(r"^replicate_(\d+)$")
_QWEN3_SLUG_RE = re.compile(r"^(qwen3_[\d.]+b)_(?:non)?reasoning$")
_TASK_NAME_RE = re.compile(r"^samples_(.+)_\d{4}-\d{2}-\d{2}T.*\.jsonl$")
_RUN_TIMESTAMP_DIR_RE = re.compile(r"^(\d{8})T(\d{6})Z$")


def _duplicate_task_files(sample_files: list[Path]) -> dict[str, list[Path]]:
    """Group `sample_files` by task name (stripping the harness's own
    per-run timestamp suffix); returns only tasks with more than one
    file — a sign that an old run's output was never actually replaced by
    a newer one. Found 2026-09-14: copying a "fresh" pilot run's output
    over an existing directory doesn't overwrite anything, since
    lm-eval-harness timestamps every filename uniquely — a stale run's
    files and a fresh run's files for the same task end up sitting side
    by side, and scoring both silently double-counts that task."""
    by_task: dict[str, list[Path]] = defaultdict(list)
    for f in sample_files:
        match = _TASK_NAME_RE.match(f.name)
        task = match.group(1) if match else f.name
        by_task[task].append(f)
    return {task: files for task, files in by_task.items() if len(files) > 1}


def _reasoning_mode_from_slug(slug: str) -> str | None:
    if slug.endswith("_reasoning"):
        return "enabled"
    if slug.endswith("_nonreasoning"):
        return "disabled"
    return None


def _correct_qwen3_provenance(slug: str) -> tuple[str, str] | None:
    """Qwen3 runs are routed entirely through llama.cpp (ADR 0010,
    Limitations 12.11) with a generic `model=llamacpp` placeholder in
    `--model_args` -- the server's own name, not the model actually
    served -- so the aggregated results_*.json's `model_name` field is
    wrong for every Qwen3 run, and `infer_backend`'s URL-port heuristic is
    fragile across machines (found 2026-09-14: a real run used port 8090,
    matching neither of infer_backend's hardcoded 8080/8081 checks,
    scoring `backend` as "unknown"). The directory slug is the one place
    that correctly records which model actually ran; derive the
    Ollama-tag-style identity from it (matching every other registered
    model's naming, e.g. "llama3.2:1b") rather than trusting either
    field. Returns None for non-Qwen3 slugs, where both fields are
    already correct.
    """
    match = _QWEN3_SLUG_RE.match(slug)
    if not match:
        return None
    size = match.group(1).split("_", 1)[1]  # "1.7b" / "4b"
    return f"qwen3:{size}", "llamacpp"


def _run_timestamp_from_pilot_root(pilot_root: Path) -> str | None:
    """`pilot_root`'s own directory name is the UTC run-start timestamp
    (`scripts/run_pilot_*.sh`'s `RUN_TIMESTAMP`, e.g. `20260915T195159Z`)
    whenever the caller points `--pilot-root` at that timestamped
    subfolder rather than `results/pilot` itself -- the documented usage
    for scoring one specific run. Used only as a fallback run_timestamp
    when a run has no aggregated `results_*.json` of its own to read one
    from (see `_fallback_provenance`); returns `None` if the directory
    name doesn't match, rather than guessing."""
    match = _RUN_TIMESTAMP_DIR_RE.match(pilot_root.name)
    if not match:
        return None
    try:
        dt = datetime.strptime(pilot_root.name, "%Y%m%dT%H%M%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None
    return dt.isoformat()


def _fallback_provenance(
    *,
    pilot_root: Path,
    slug: str,
    corpus_version: str,
    reasoning_mode: str | None,
    replicate_index: int,
) -> RunProvenance | None:
    """Build a RunProvenance for a run with sample files but no aggregated
    `results_*.json` -- a total failure every attempt crashed on before
    lm-eval-harness ever wrote one, reconciled by `robust_run.py` into
    explicit `*.missing.jsonl` stubs for every item (9.3) rather than
    losing the condition silently. `provenance_from_aggregated_results`
    has nothing to read in this case, so identity is recovered the same
    way `_correct_qwen3_provenance` already recovers it for a *completed*
    Qwen3 run: from the directory slug, since Qwen3's `--model_args` uses
    a generic `model=llamacpp` placeholder either way -- the aggregated
    file was never the real source of truth for Qwen3 identity, only for
    the run timestamp, which falls back to `pilot_root`'s own name.
    Returns `None` if the slug isn't a recognised Qwen3 condition, since
    every other model's real identity genuinely lives only in the missing
    results.json -- an unrecoverable case, not a guess to paper over.
    """
    corrected = _correct_qwen3_provenance(slug)
    if corrected is None:
        return None
    model_name, backend = corrected
    return RunProvenance(
        corpus_version=corpus_version,
        model_name=model_name,
        backend=backend,
        run_timestamp=_run_timestamp_from_pilot_root(pilot_root) or "unknown",
        reasoning_mode=reasoning_mode,
        replicate_index=replicate_index,
    )


def find_runs(pilot_root: Path):
    """Yield (slug, replicate_index, run_dir) for every scored-able run
    directory under `pilot_root` — one per (model/condition, replicate)."""
    for slug_dir in sorted(pilot_root.iterdir()):
        if not slug_dir.is_dir():
            continue
        for replicate_dir in sorted(slug_dir.glob("replicate_*")):
            match = _REPLICATE_RE.match(replicate_dir.name)
            if not match or not replicate_dir.is_dir():
                continue
            replicate_index = int(match.group(1))
            model_dirs = [
                d for d in replicate_dir.iterdir() if d.is_dir() and d.name != ".cache"
            ]
            for model_dir in model_dirs:
                yield slug_dir.name, replicate_index, model_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--pilot-root", required=True, type=Path, help="e.g. results/pilot"
    )
    parser.add_argument("--corpus-version", default="v0.3")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--no-auto-digest", action="store_true")
    args = parser.parse_args(argv)

    if not args.pilot_root.is_dir():
        print(f"error: --pilot-root does not exist: {args.pilot_root}", file=sys.stderr)
        return 1

    all_results = []
    digest_cache: dict[tuple[str, str], str | None] = {}
    run_count = 0

    for slug, replicate_index, run_dir in find_runs(args.pilot_root):
        results_jsons = sorted(run_dir.glob("results_*.json"))
        sample_files = sorted(run_dir.glob("samples_*.jsonl"))
        if not sample_files:
            print(
                f"skipping {run_dir} (no samples_*.jsonl at all — nothing to score)",
                file=sys.stderr,
            )
            continue

        duplicates = _duplicate_task_files(sample_files)
        if duplicates:
            print(
                f"skipping {run_dir}: more than one samples file for the "
                f"same task(s) -- {sorted(duplicates)}. This usually means "
                "a copy from another machine/run landed alongside an "
                "older attempt's leftover output rather than replacing it "
                "(lm-eval-harness timestamps every filename uniquely, so "
                "a plain file copy never overwrites). Remove the stale "
                "(older-timestamped) files and re-run.",
                file=sys.stderr,
            )
            continue

        reasoning_mode = _reasoning_mode_from_slug(slug)

        if results_jsons:
            provenance = provenance_from_aggregated_results(
                results_jsons[-1],
                corpus_version=args.corpus_version,
                reasoning_mode=reasoning_mode,
                replicate_index=replicate_index,
            )
            corrected = _correct_qwen3_provenance(slug)
            if corrected is not None:
                provenance.model_name, provenance.backend = corrected
        else:
            # No aggregated results_*.json -- every attempt crashed before
            # lm-eval-harness wrote one, and robust_run.py reconciled the
            # condition into explicit *.missing.jsonl stubs instead (9.3).
            # This is a real, scoreable total-failure condition (10.7's
            # Infrastructure-Failure rate), not nothing to report --
            # silently dropping it here would understate that rate for
            # this condition as if it were never tested at all.
            provenance = _fallback_provenance(
                pilot_root=args.pilot_root,
                slug=slug,
                corpus_version=args.corpus_version,
                reasoning_mode=reasoning_mode,
                replicate_index=replicate_index,
            )
            if provenance is None:
                print(
                    f"skipping {run_dir}: no results_*.json and slug "
                    f"{slug!r} isn't a recognised Qwen3 condition, so "
                    "model identity can't be recovered from the slug "
                    "alone -- a genuine total failure with no way to "
                    "attribute it to a specific model/backend.",
                    file=sys.stderr,
                )
                continue

        if provenance.model_digest is None and not args.no_auto_digest:
            cache_key = (provenance.model_name, provenance.backend)
            if cache_key not in digest_cache:
                digest_cache[cache_key] = auto_detect_model_digest(
                    provenance.model_name, provenance.backend
                )
            provenance.model_digest = digest_cache[cache_key]

        run_count += 1
        print(
            f"[{run_count}] scoring {slug}/replicate_{replicate_index:03d} "
            f"({len(sample_files)} task file(s))",
            file=sys.stderr,
        )
        for sample_file in sample_files:
            all_results.extend(score_jsonl_file(sample_file, provenance))

    write_scored_jsonl(all_results, args.out)
    print(
        f"\nwrote {len(all_results)} scored rows from {run_count} run(s) to {args.out}",
        file=sys.stderr,
    )

    category_counts: dict[str, int] = {}
    for result in all_results:
        category_counts[result.scored.category.value] = (
            category_counts.get(result.scored.category.value, 0) + 1
        )
    print("category breakdown:", file=sys.stderr)
    for category, count in sorted(category_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {category}: {count}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
