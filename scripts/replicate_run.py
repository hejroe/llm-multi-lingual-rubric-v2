#!/usr/bin/env python3
"""Run the same task(s) against the same model N times — STUDY_PROTOCOL.md
9.3's replication, whose stated 3 is this pilot's own starting value, not
a ceiling on N itself (ADR 0003: "starting scale, not a ceiling"). Someone
wanting to demonstrate answer stability for their own fine-tuned model
against their own rubric might reasonably want 100 replicates rather than
3 — this script supports any N, not just the pilot's own default.

Each replicate is a fully independent re-query: its own `--use_cache`, its
own output subdirectory, and (deliberately) the *same* seed as every other
replicate and every other run in this project — matching the fixed base
parameters everywhere else. With temperature=0 (greedy decoding), any
variation across replicates therefore comes from the lower-level non-
determinism 9.3 already documents (batched inference, GPU kernel non-
associativity, serving-stack behaviour), not from a deliberately varied
seed confounding the comparison.

Usage (run INSIDE the eval container, wrapping scripts/robust_run.py) —
invoked as a module (`-m scripts.replicate_run`), not a direct file path:
this script imports `scripts.robust_run`, and a direct `python
scripts/replicate_run.py` invocation puts only the script's own directory
on sys.path, not the repo root, so that import fails (found 2026-09-12,
running it for real for the first time):

    python -m scripts.replicate_run \
      --replications 100 \
      --model local-chat-completions \
      --model_args base_url=http://host.docker.internal:11434/v1/chat/completions,model=llama3.2:1b,num_concurrent=1 \
      --apply_chat_template \
      --include_path /configs/lm_eval_tasks \
      --tasks corpus_b_en \
      --output_path /results/corpus_b_en_stability
      [any other scripts/robust_run.py flag: --limit, --run-retries, ...]

Writes one subdirectory per replicate (`<output_path>/replicate_000/`,
`replicate_001/`, ...), each independently robust — `robust_run.py`'s own
crash-retry-then-reconcile applies within every replicate. Score each
replicate directory separately with `scoring.cli` (passing
`--replicate-index <i>` — see that module), then concatenate the scored
JSONLs before calling `analysis.reliability.compute_reliability`, which
needs no special replicate-count handling: rows sharing the same
(model_name, question_id) key are the replicates, however many there are.
"""

from __future__ import annotations

import argparse
import sys

from scripts.robust_run import main as robust_run_main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--replications", type=int, default=3,
        help="Protocol 9.3's starting point is 3; any N >= 1 is supported",
    )
    parser.add_argument("--output_path", required=True)
    # Every other flag (--model, --model_args, --tasks, --limit, ...) is
    # forwarded verbatim to scripts/robust_run.py for each replicate.
    known, passthrough = parser.parse_known_args(argv)

    if known.replications < 1:
        print("error: --replications must be at least 1", file=sys.stderr)
        return 1

    width = max(3, len(str(known.replications - 1)))
    exit_codes = []
    for i in range(known.replications):
        replicate_output = f"{known.output_path.rstrip('/')}/replicate_{i:0{width}d}"
        print(f"[replicate_run] replicate {i + 1}/{known.replications} -> {replicate_output}", file=sys.stderr)
        exit_codes.append(robust_run_main([*passthrough, "--output_path", replicate_output]))

    failed = [i for i, code in enumerate(exit_codes) if code != 0]
    if failed:
        print(
            f"[replicate_run] {len(failed)}/{known.replications} replicate(s) reported a non-zero exit "
            f"(0-indexed): {failed} — each replicate's own reconciliation (robust_run.py) still records "
            "what did or didn't get a response; check each replicate_*/'s *.missing.jsonl.",
            file=sys.stderr,
        )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
