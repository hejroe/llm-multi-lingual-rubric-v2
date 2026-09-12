"""Tests for scripts/replicate_run.py's own orchestration logic (directory
naming, argument forwarding, exit-code aggregation) — mocking
scripts.robust_run.main, since a real invocation needs lm_eval/datasets
inside the eval container (see scripts/robust_run.py's own test file for
why that part isn't unit-tested locally)."""

from unittest.mock import patch

from scripts.replicate_run import main


def test_replicates_into_numbered_subdirectories():
    with patch("scripts.replicate_run.robust_run_main", return_value=0) as mock_main:
        exit_code = main([
            "--replications", "3",
            "--output_path", "/results/stability_test",
            "--model", "local-chat-completions",
            "--model_args", "model=x",
            "--tasks", "corpus_b_en",
            "--include_path", "/configs/lm_eval_tasks",
        ])

    assert exit_code == 0
    assert mock_main.call_count == 3
    output_paths = []
    for call in mock_main.call_args_list:
        forwarded_args = call.args[0]
        output_paths.append(forwarded_args[forwarded_args.index("--output_path") + 1])
    assert output_paths == [
        "/results/stability_test/replicate_000",
        "/results/stability_test/replicate_001",
        "/results/stability_test/replicate_002",
    ]


def test_forwards_other_flags_unchanged():
    with patch("scripts.replicate_run.robust_run_main", return_value=0) as mock_main:
        main([
            "--replications", "1",
            "--output_path", "/results/x",
            "--model_args", "model=x,timeout=60",
            "--limit", "5",
        ])
    forwarded_args = mock_main.call_args_list[0].args[0]
    assert "--model_args" in forwarded_args
    assert forwarded_args[forwarded_args.index("--model_args") + 1] == "model=x,timeout=60"
    assert "--limit" in forwarded_args
    assert forwarded_args[forwarded_args.index("--limit") + 1] == "5"


def test_supports_large_replication_counts_with_padded_names():
    with patch("scripts.replicate_run.robust_run_main", return_value=0) as mock_main:
        main(["--replications", "100", "--output_path", "/results/x"])
    forwarded_args = mock_main.call_args_list[-1].args[0]
    assert forwarded_args[forwarded_args.index("--output_path") + 1] == "/results/x/replicate_099"


def test_nonzero_when_any_replicate_fails():
    with patch("scripts.replicate_run.robust_run_main", side_effect=[0, 1, 0]):
        exit_code = main(["--replications", "3", "--output_path", "/results/x"])
    assert exit_code == 1


def test_rejects_zero_or_negative_replications():
    exit_code = main(["--replications", "0", "--output_path", "/results/x"])
    assert exit_code == 1
