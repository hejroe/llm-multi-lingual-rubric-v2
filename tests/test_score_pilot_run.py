from pathlib import Path

from scoring.score_pilot_run import (
    _correct_qwen3_provenance,
    _duplicate_task_files,
    _fallback_provenance,
    _reasoning_mode_from_slug,
    _run_timestamp_from_pilot_root,
    find_runs,
)


def test_reasoning_mode_from_slug():
    assert _reasoning_mode_from_slug("qwen3_4b_reasoning") == "enabled"
    assert _reasoning_mode_from_slug("qwen3_4b_nonreasoning") == "disabled"
    assert _reasoning_mode_from_slug("llama3.2_1b") is None


def test_correct_qwen3_provenance_derives_size_and_backend_from_slug():
    # Regression (2026-09-14): real pilot data showed model_name="llamacpp"
    # (the server, not the model) for every Qwen3 run, and backend
    # "unknown" (infer_backend's hardcoded 8080/8081 check didn't match a
    # real run's port 8090) -- both wrong in the same way, for the same
    # underlying reason: --model_args used a generic "llamacpp" placeholder.
    assert _correct_qwen3_provenance("qwen3_1.7b_nonreasoning") == (
        "qwen3:1.7b",
        "llamacpp",
    )
    assert _correct_qwen3_provenance("qwen3_1.7b_reasoning") == (
        "qwen3:1.7b",
        "llamacpp",
    )
    assert _correct_qwen3_provenance("qwen3_4b_nonreasoning") == (
        "qwen3:4b",
        "llamacpp",
    )


def test_correct_qwen3_provenance_none_for_non_qwen3_slugs():
    # Every other model's aggregated results_*.json already carries its
    # real model_name/backend correctly -- nothing to override.
    assert _correct_qwen3_provenance("llama3.2_1b") is None
    assert _correct_qwen3_provenance("phi4-mini") is None


def test_find_runs_walks_slug_replicate_model_structure(tmp_path):
    # results/pilot/<slug>/replicate_NNN/<sanitized-model>/
    for slug, replicate, model_dir_name in [
        ("llama3.2_1b", "replicate_000", "llama3.2__1b"),
        ("llama3.2_1b", "replicate_001", "llama3.2__1b"),
        ("qwen3_4b_reasoning", "replicate_000", "llamacpp"),
    ]:
        d = tmp_path / slug / replicate / model_dir_name
        d.mkdir(parents=True)
        (d / ".cache_rank0.db").write_text(
            ""
        )  # should be ignored, not a real model dir

    runs = sorted(find_runs(tmp_path))
    assert runs == [
        ("llama3.2_1b", 0, tmp_path / "llama3.2_1b" / "replicate_000" / "llama3.2__1b"),
        ("llama3.2_1b", 1, tmp_path / "llama3.2_1b" / "replicate_001" / "llama3.2__1b"),
        (
            "qwen3_4b_reasoning",
            0,
            tmp_path / "qwen3_4b_reasoning" / "replicate_000" / "llamacpp",
        ),
    ]


def test_find_runs_ignores_cache_directory(tmp_path):
    slug_dir = tmp_path / "llama3.2_1b" / "replicate_000"
    (slug_dir / ".cache").mkdir(parents=True)
    (slug_dir / "llama3.2__1b").mkdir(parents=True)

    runs = list(find_runs(tmp_path))
    assert len(runs) == 1
    assert runs[0][2].name == "llama3.2__1b"


def test_find_runs_skips_non_replicate_directories(tmp_path):
    (tmp_path / "llama3.2_1b" / "not_a_replicate_dir").mkdir(parents=True)
    runs = list(find_runs(tmp_path))
    assert runs == []


def test_duplicate_task_files_detects_stale_plus_fresh_pair():
    # Regression (2026-09-14): a real pilot run had exactly this shape --
    # an old (pre-crash) attempt's samples file for a task sitting
    # alongside a freshly copied-in one for the same task, both with
    # different timestamps in the filename.
    files = [
        Path("samples_corpus_a_knowledge_en_2026-09-12T23-30-43.983931.jsonl"),
        Path("samples_corpus_a_knowledge_en_2026-09-13T15-24-25.935606.jsonl"),
        Path("samples_corpus_b_en_2026-09-13T15-24-25.935606.jsonl"),
    ]
    duplicates = _duplicate_task_files(files)
    assert list(duplicates.keys()) == ["corpus_a_knowledge_en"]
    assert len(duplicates["corpus_a_knowledge_en"]) == 2


def test_duplicate_task_files_empty_when_one_file_per_task():
    files = [
        Path("samples_corpus_a_knowledge_en_2026-09-13T15-24-25.935606.jsonl"),
        Path("samples_corpus_b_en_2026-09-13T15-24-25.935606.jsonl"),
    ]
    assert _duplicate_task_files(files) == {}


def test_run_timestamp_from_pilot_root_parses_timestamped_folder():
    # scripts/run_pilot_*.sh's RUN_TIMESTAMP folder format.
    ts = _run_timestamp_from_pilot_root(Path("results/pilot/20260915T195159Z"))
    assert ts == "2026-09-15T19:51:59+00:00"


def test_run_timestamp_from_pilot_root_none_for_non_timestamped_folder():
    # e.g. --pilot-root results/pilot itself, or the pre-timestamping v0.2
    # layout -- no reliable timestamp to fall back to.
    assert _run_timestamp_from_pilot_root(Path("results/pilot")) is None


def test_fallback_provenance_recovers_qwen3_identity_without_results_json():
    # Regression (2026-09-18): a real corpus-v0.3 run had qwen3_4b_nonreasoning
    # crash on every one of 3 replicates before lm-eval-harness ever wrote an
    # aggregated results_*.json -- robust_run.py correctly reconciled the
    # condition into *.missing.jsonl stubs for every item (9.3), but
    # score_pilot_run.py had nothing to build a RunProvenance from, and
    # silently dropped the entire condition from the scored output instead
    # of reporting it as 100% Infrastructure-Failure (10.7).
    provenance = _fallback_provenance(
        pilot_root=Path("results/pilot/20260915T195159Z"),
        slug="qwen3_4b_nonreasoning",
        corpus_version="v0.3",
        reasoning_mode="disabled",
        replicate_index=0,
    )
    assert provenance is not None
    assert provenance.model_name == "qwen3:4b"
    assert provenance.backend == "llamacpp"
    assert provenance.run_timestamp == "2026-09-15T19:51:59+00:00"
    assert provenance.reasoning_mode == "disabled"
    assert provenance.replicate_index == 0


def test_fallback_provenance_none_for_unrecoverable_non_qwen3_slug():
    # Every non-Qwen3 model's real identity lives only in the missing
    # results.json -- genuinely unrecoverable from the slug alone, so this
    # must be skipped rather than guessed.
    assert (
        _fallback_provenance(
            pilot_root=Path("results/pilot/20260915T195159Z"),
            slug="llama3.2_1b",
            corpus_version="v0.3",
            reasoning_mode=None,
            replicate_index=0,
        )
        is None
    )
