from scoring.score_pilot_run import (
    _correct_qwen3_provenance,
    _reasoning_mode_from_slug,
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
