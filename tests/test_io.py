import json

from scoring.categories import JurisdictionAdaptation, PrimaryCategory
from scoring.io import (
    RunProvenance,
    _base_fact_id,
    infer_backend,
    provenance_from_aggregated_results,
    read_samples,
    score_jsonl_file,
    write_scored_jsonl,
)


def _write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _sample(doc, response_text):
    # Mirrors the real shape observed from lm-eval-harness's --log_samples
    # output (2026-09-12): resps is a list of one list of candidate texts.
    return {
        "doc_id": 0,
        "doc": doc,
        "target": doc.get("gold_answer", ""),
        "resps": [[response_text]] if response_text is not None else [[]],
        "filtered_resps": [response_text] if response_text is not None else ["[invalid]"],
    }


def test_base_fact_id_parses_jurisdiction_and_version_variants():
    assert _base_fact_id("B-ALC-01-unspecified-en") == "B-ALC-01"
    assert _base_fact_id("B-ALC-01-UK-en") == "B-ALC-01"
    assert _base_fact_id("C-CT-01-v1-en") == "C-CT-01"
    assert _base_fact_id("C-CT-01-v2-en") == "C-CT-01"


def test_infer_backend():
    assert infer_backend("http://host.docker.internal:11434/v1/chat/completions") == "ollama"
    assert infer_backend("http://localhost:8081/v1/chat/completions") == "llamacpp"


def test_score_jsonl_file_knowledge_item(tmp_path):
    doc = {
        "question_id": "A-KNOW-01-de", "family": "A", "domain": "knowledge", "language": "de",
        "question_text": "Was ist das Kraftwerk der Zelle?", "gold_answer": "Mitochondrien",
        "tool_required": "no",
    }
    jsonl_path = tmp_path / "samples_corpus_a_knowledge_de_2026-01-01.jsonl"
    _write_jsonl(jsonl_path, [_sample(doc, "Die Mitochondrien.")])

    provenance = RunProvenance(
        corpus_version="v0.2", model_name="llama3.2:1b", backend="ollama",
        run_timestamp="2026-09-12T00:00:00+00:00",
    )
    results = score_jsonl_file(jsonl_path, provenance)

    assert len(results) == 1
    assert results[0].scored.category == PrimaryCategory.CORRECT
    assert results[0].provenance.corpus_version == "v0.2"


def test_score_jsonl_file_empty_response_is_infrastructure_failure(tmp_path):
    doc = {
        "question_id": "A-KNOW-01-en", "family": "A", "domain": "knowledge", "language": "en",
        "question_text": "What is the powerhouse of the cell?", "gold_answer": "mitochondria",
        "tool_required": "no",
    }
    jsonl_path = tmp_path / "samples.jsonl"
    _write_jsonl(jsonl_path, [_sample(doc, None)])

    provenance = RunProvenance(
        corpus_version="v0.2", model_name="llama3.2:1b", backend="ollama",
        run_timestamp="2026-09-12T00:00:00+00:00",
    )
    results = score_jsonl_file(jsonl_path, provenance)
    assert results[0].scored.category == PrimaryCategory.INFRASTRUCTURE_FAILURE


def test_score_jsonl_file_builds_jurisdiction_siblings_from_same_file(tmp_path):
    # One task's JSONL already contains every jurisdiction variant for a
    # language (ADR 0009) — siblings must come from within the same file,
    # not a separate corpus load.
    unspecified = {
        "question_id": "B-ALC-01-unspecified-en", "family": "B", "language": "en",
        "jurisdiction": "", "gold_answer": "", "question_text": "Minimum age to buy alcohol?",
    }
    uk = {
        "question_id": "B-ALC-01-UK-en", "family": "B", "language": "en",
        "jurisdiction": "the United Kingdom", "gold_answer": "18",
        "question_text": "Minimum age to buy alcohol in the UK?",
    }
    us = {
        "question_id": "B-ALC-01-US-en", "family": "B", "language": "en",
        "jurisdiction": "the United States", "gold_answer": "21",
        "question_text": "Minimum age to buy alcohol in the US?",
    }
    jsonl_path = tmp_path / "samples_corpus_b_en.jsonl"
    _write_jsonl(jsonl_path, [
        _sample(unspecified, "18"),  # defaults to the UK's answer
        _sample(uk, "18"),
        _sample(us, "21"),
    ])

    provenance = RunProvenance(
        corpus_version="v0.2", model_name="llama3.2:1b", backend="ollama",
        run_timestamp="2026-09-12T00:00:00+00:00",
    )
    results = score_jsonl_file(jsonl_path, provenance)
    by_id = {r.scored.question_id: r.scored for r in results}

    assert by_id["B-ALC-01-unspecified-en"].jurisdiction_adaptation == JurisdictionAdaptation.WRONG_JURISDICTION_DEFAULT
    assert by_id["B-ALC-01-UK-en"].jurisdiction_adaptation == JurisdictionAdaptation.CORRECT_FOR_JURISDICTION
    assert by_id["B-ALC-01-US-en"].jurisdiction_adaptation == JurisdictionAdaptation.CORRECT_FOR_JURISDICTION


def test_provenance_from_aggregated_results(tmp_path):
    aggregated = {
        "config": {"model_args": {"base_url": "http://host.docker.internal:11434/v1/chat/completions", "model": "llama3.2:1b"}},
        "model_name": "llama3.2:1b",
        "date": 1789224420.0,
    }
    path = tmp_path / "results_2026-01-01.json"
    path.write_text(json.dumps(aggregated), encoding="utf-8")

    provenance = provenance_from_aggregated_results(path, corpus_version="v0.2", model_digest="abc123")
    assert provenance.model_name == "llama3.2:1b"
    assert provenance.backend == "ollama"
    assert provenance.corpus_version == "v0.2"
    assert provenance.model_digest == "abc123"


def test_write_scored_jsonl_round_trips(tmp_path):
    doc = {
        "question_id": "A-KNOW-01-en", "family": "A", "domain": "knowledge", "language": "en",
        "question_text": "What is the powerhouse of the cell?", "gold_answer": "mitochondria",
        "tool_required": "no",
    }
    jsonl_path = tmp_path / "samples.jsonl"
    _write_jsonl(jsonl_path, [_sample(doc, "The mitochondria.")])

    provenance = RunProvenance(
        corpus_version="v0.2", model_name="llama3.2:1b", backend="ollama",
        run_timestamp="2026-09-12T00:00:00+00:00",
    )
    results = score_jsonl_file(jsonl_path, provenance)
    out_path = tmp_path / "scored.jsonl"
    write_scored_jsonl(results, out_path)

    written = read_samples(out_path)
    assert written[0]["question_id"] == "A-KNOW-01-en"
    assert written[0]["category"] == "Correct"
    assert written[0]["corpus_version"] == "v0.2"
    # Item-context fields the analysis layer needs for pairing (Section 10)
    # must be carried through, not just the scoring result.
    assert written[0]["family"] == "A"
    assert written[0]["language"] == "en"
