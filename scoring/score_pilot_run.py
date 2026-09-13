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
from pathlib import Path

from scoring.io import (
    auto_detect_model_digest,
    provenance_from_aggregated_results,
    score_jsonl_file,
    write_scored_jsonl,
)

_REPLICATE_RE = re.compile(r"^replicate_(\d+)$")


def _reasoning_mode_from_slug(slug: str) -> str | None:
    if slug.endswith("_reasoning"):
        return "enabled"
    if slug.endswith("_nonreasoning"):
        return "disabled"
    return None


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
    parser.add_argument("--corpus-version", default="v0.2")
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
        if not results_jsons or not sample_files:
            print(
                f"skipping {run_dir} (no results_*.json/samples_*.jsonl — "
                "likely a total failure)",
                file=sys.stderr,
            )
            continue

        reasoning_mode = _reasoning_mode_from_slug(slug)
        provenance = provenance_from_aggregated_results(
            results_jsons[-1],
            corpus_version=args.corpus_version,
            reasoning_mode=reasoning_mode,
            replicate_index=replicate_index,
        )

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
