"""Tests for analysis.cli: per-model grouping (10.2's reporting grain) and
the end-to-end report over a small multi-model scored dataset.
"""

import json

from analysis.cli import _model_groups, main


def _row(question_id, category, model_name, **extra):
    row = {
        "question_id": question_id,
        "category": category,
        "model_name": model_name,
    }
    row.update(extra)
    return row


def test_model_groups_treats_reasoning_mode_as_part_of_the_key():
    # Regression (2026-09-14): ADR 0010 treats Qwen3's non-reasoning and
    # reasoning conditions as two conditions that must never be pooled --
    # grouping by model_name alone would merge them back together.
    rows = [
        _row("A-1-en", "Correct", "qwen3:1.7b", reasoning_mode="disabled"),
        _row("A-1-en", "Correct", "qwen3:1.7b", reasoning_mode="enabled"),
        _row("A-1-en", "Correct", "llama3.2:1b"),
    ]
    groups = _model_groups(rows)
    assert groups == [
        ("llama3.2:1b", None),
        ("qwen3:1.7b", "disabled"),
        ("qwen3:1.7b", "enabled"),
    ]


def test_main_reports_each_model_separately(tmp_path, capsys):
    # Regression (2026-09-14): found via real multi-model pilot data --
    # main() previously pooled every model's rows into one set of RQ
    # results; each registered model must get its own section.
    rows = [
        _row(
            "A-1-en",
            "Correct",
            "llama3.2:1b",
            family="A",
            domain="knowledge",
            language="en",
        ),
        _row(
            "A-1-de",
            "Incorrect-Guess",
            "llama3.2:1b",
            family="A",
            domain="knowledge",
            language="de",
            language_variant_of="A-1-en",
        ),
        _row(
            "A-1-en",
            "Correct",
            "phi4-mini",
            family="A",
            domain="knowledge",
            language="en",
        ),
        _row(
            "A-1-de",
            "Correct",
            "phi4-mini",
            family="A",
            domain="knowledge",
            language="de",
            language_variant_of="A-1-en",
        ),
    ]
    scored_path = tmp_path / "scored.jsonl"
    with open(scored_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    exit_code = main(["--scored", str(scored_path)])
    assert exit_code == 0

    out = capsys.readouterr().out
    assert "llama3.2:1b" in out
    assert "phi4-mini" in out
    # Each model's own RQ1 line should reflect only that model's rows.
    assert "en=100.0%, de=0.0%" in out  # llama3.2:1b: discordant
    assert "en=100.0%, de=100.0%" in out  # phi4-mini: concordant
