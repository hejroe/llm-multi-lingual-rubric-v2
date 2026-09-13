"""Tests for scoring.cli's `main` entry point: provenance construction
from an aggregated results_*.json, the total-failure fallback path, and
the scored-JSONL output it writes.
"""

import json

from scoring.categories import PrimaryCategory
from scoring.cli import main


def _write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_scores_total_failure_run_with_explicit_provenance(tmp_path):
    # scripts/robust_run.py's reconciliation writes a *.missing.jsonl with
    # no results_*.json alongside it when a run crashes before producing
    # any real output at all (found 2026-09-12) — scoring.cli must still
    # be able to score it, given explicit provenance since there's no
    # aggregated results file to read it from.
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    doc = {
        "question_id": "B-ALC-01-unspecified-en",
        "family": "B",
        "language": "en",
        "jurisdiction": "",
        "gold_answer": "",
        "question_text": "Minimum age to buy alcohol?",
    }
    _write_jsonl(
        run_dir / "samples_corpus_b_en_norun.missing.jsonl",
        [{"doc": doc, "resps": [[]], "filtered_resps": ["[no_response]"]}],
    )

    out_path = tmp_path / "scored.jsonl"
    exit_code = main(
        [
            "--run-dir",
            str(run_dir),
            "--corpus-version",
            "v0.2",
            "--out",
            str(out_path),
            "--model-name",
            "llama3.2:1b",
            "--backend",
            "ollama",
            "--no-auto-digest",  # keep this test hermetic — no real network/file I/O
        ]
    )

    assert exit_code == 0
    with open(out_path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    assert len(rows) == 1
    assert rows[0]["category"] == PrimaryCategory.INFRASTRUCTURE_FAILURE.value
    assert rows[0]["model_name"] == "llama3.2:1b"
    assert rows[0]["backend"] == "ollama"


def test_refuses_total_failure_run_without_explicit_provenance(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_jsonl(
        run_dir / "samples_corpus_b_en_norun.missing.jsonl",
        [
            {
                "doc": {"question_id": "x", "family": "B"},
                "resps": [[]],
                "filtered_resps": ["[no_response]"],
            }
        ],
    )
    exit_code = main(
        [
            "--run-dir",
            str(run_dir),
            "--corpus-version",
            "v0.2",
            "--out",
            str(tmp_path / "scored.jsonl"),
        ]
    )
    assert exit_code == 1


def test_refuses_empty_run_dir(tmp_path):
    run_dir = tmp_path / "empty"
    run_dir.mkdir()
    exit_code = main(
        [
            "--run-dir",
            str(run_dir),
            "--corpus-version",
            "v0.2",
            "--out",
            str(tmp_path / "scored.jsonl"),
        ]
    )
    assert exit_code == 1
