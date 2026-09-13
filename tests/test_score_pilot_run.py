from scoring.score_pilot_run import _reasoning_mode_from_slug, find_runs


def test_reasoning_mode_from_slug():
    assert _reasoning_mode_from_slug("qwen3_4b_reasoning") == "enabled"
    assert _reasoning_mode_from_slug("qwen3_4b_nonreasoning") == "disabled"
    assert _reasoning_mode_from_slug("llama3.2_1b") is None


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
