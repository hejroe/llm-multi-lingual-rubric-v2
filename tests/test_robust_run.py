"""Tests for the parts of scripts/robust_run.py that don't need lm_eval or
datasets installed (those are only available inside the eval container —
see that module's own docstring for why the reconciliation logic that
does need them isn't unit-tested locally)."""

from unittest.mock import patch

from scripts.robust_run import build_lm_eval_args, ensure_resilience_args, main


def test_ensure_resilience_args_injects_defaults_when_absent():
    result = ensure_resilience_args(
        "base_url=http://x,model=llama3.2:1b,num_concurrent=1"
    )
    assert "timeout=120" in result
    assert "max_retries=2" in result


def test_ensure_resilience_args_respects_caller_overrides():
    result = ensure_resilience_args("model=x,timeout=60,max_retries=5")
    assert "timeout=60" in result
    assert "max_retries=5" in result
    # not duplicated with the default
    assert result.count("timeout=") == 1
    assert result.count("max_retries=") == 1


class _Args:
    def __init__(self, **kwargs):
        self.model = "local-chat-completions"
        self.model_args = "model=x"
        self.tasks = "corpus_b_en"
        self.include_path = "/configs/lm_eval_tasks"
        self.output_path = "/results/foo"
        self.apply_chat_template = False
        self.limit = None
        self.gen_kwargs = None
        self.__dict__.update(kwargs)


def test_build_lm_eval_args_includes_log_samples_and_cache():
    args = build_lm_eval_args(_Args())
    assert "--log_samples" in args
    assert "--use_cache" in args
    cache_idx = args.index("--use_cache")
    assert args[cache_idx + 1] == "/results/foo/.cache"


def test_build_lm_eval_args_optional_flags():
    args = build_lm_eval_args(_Args(apply_chat_template=True, limit=5.0))
    assert "--apply_chat_template" in args
    assert "--limit" in args
    limit_idx = args.index("--limit")
    assert args[limit_idx + 1] == "5.0"


def test_build_lm_eval_args_omits_limit_when_not_set():
    args = build_lm_eval_args(_Args())
    assert "--limit" not in args


def test_build_lm_eval_args_forwards_gen_kwargs_when_set():
    gen_kwargs = '{"chat_template_kwargs": {"enable_thinking": false}}'
    args = build_lm_eval_args(_Args(gen_kwargs=gen_kwargs))
    assert "--gen_kwargs" in args
    idx = args.index("--gen_kwargs")
    assert args[idx + 1] == gen_kwargs


def test_build_lm_eval_args_omits_gen_kwargs_when_not_set():
    args = build_lm_eval_args(_Args())
    assert "--gen_kwargs" not in args


def test_main_accepts_gen_kwargs_without_raising(tmp_path):
    # Regression (2026-09-13): this script's argparse previously had no
    # --gen_kwargs option at all, so scripts/run_pilot_qwen3_llamacpp.sh's
    # non-reasoning condition (the primary, pre-registered one, ADR 0010)
    # crashed with SystemExit(2) ("unrecognized arguments") before lm_eval
    # was ever invoked. `model_output_subdir` is stubbed out since it
    # imports lm_eval.utils (only available inside the eval container);
    # include_path deliberately has no matching task YAML, so
    # reconcile_task no-ops without needing lm_eval/datasets either.
    include_path = tmp_path / "no_tasks_here"
    include_path.mkdir()
    with (
        patch("subprocess.run") as mock_run,
        patch("scripts.robust_run.model_output_subdir", return_value=tmp_path / "out"),
    ):
        mock_run.return_value.returncode = 0
        exit_code = main(
            [
                "--model",
                "local-chat-completions",
                "--model_args",
                "model=x",
                "--tasks",
                "corpus_b_en",
                "--include_path",
                str(include_path),
                "--output_path",
                str(tmp_path / "out"),
                "--gen_kwargs",
                '{"chat_template_kwargs": {"enable_thinking": false}}',
            ]
        )
    assert exit_code == 0
    called_lm_eval_args = mock_run.call_args[0][0]
    assert "--gen_kwargs" in called_lm_eval_args
