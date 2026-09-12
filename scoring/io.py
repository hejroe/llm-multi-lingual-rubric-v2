"""Join lm-evaluation-harness `--log_samples` output to the scoring rubric,
with STUDY_PROTOCOL.md 9.6 run-level provenance stamping.

Design note (found while building this): this project's custom harness
tasks (ADR 0009) load each corpus CSV directly via the `csv` dataset
loader, so a sample's own `doc` field already carries every corpus column
verbatim (question_id, family, gold_answer, etc.) — no separate corpus
CSV load/join is needed for the item itself. It IS still needed for the
8.3 overlay axes' *sibling* rows (Set B's other jurisdiction variants, Set
C's other effective-date versions of the same fact) — but since one task
file covers one whole language already, those siblings are simply the
*other rows already in the same JSONL file*, grouped by a shared base-fact
id derived from `question_id` (see `_base_fact_id`).

`local-chat-completions`'s own tenacity-based retry either succeeds
silently or raises and crashes the whole `lm_eval` run — it does not
surface a per-item error/timeout signal into `--log_samples` the way
8.2/9.3 assume, so `is_infrastructure_failure` (scoring/rubric.py) only
ever sees an empty response, never an explicit harness-reported error,
from a *raw* harness invocation. Run evaluations through
`scripts/robust_run.py` (not `lm_eval` directly) to close that gap — it
reconciles a crashed run's still-missing items into explicit empty-
response stubs this module already handles correctly.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from scoring.rubric import ScoredResponse, score_response

RUBRIC_VERSION = "0.3"


@dataclass
class RunProvenance:
    """STUDY_PROTOCOL.md 9.6's required run-level stamp."""

    corpus_version: str
    model_name: str
    backend: str
    run_timestamp: str  # ISO 8601
    rubric_version: str = RUBRIC_VERSION
    model_digest: str | None = None  # not recoverable from harness output; supply from `ollama list`
    param_overrides: str | None = None
    tool_mode: str | None = None  # "simulated" | "live", Set D only (9.5)
    reasoning_mode: str | None = None  # "enabled" | "disabled", Qwen3 only (ADR 0010, 9.3)
    replicate_index: int | None = None  # which of N replications (9.3, scripts/replicate_run.py) this run is


def read_samples(jsonl_path: Path) -> list[dict]:
    samples = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def _raw_response_text(sample: dict) -> str | None:
    """The model's raw completion, before lm-eval-harness's own answer-
    extraction filter — this project's rubric scores the raw text (8.4),
    not the harness's `filtered_resps`."""
    resps = sample.get("resps")
    if not resps or not resps[0]:
        return None
    return resps[0][0]


_BASE_FACT_ID_RE = re.compile(r"^(?P<base>.+)-(?P<variant>[^-]+)-(?P<lang>[a-z]{2})$")


def _base_fact_id(question_id: str) -> str | None:
    """Set B/C question_ids follow `{base}-{variant}-{lang}` (e.g.
    `B-ALC-01-unspecified-en`, `B-ALC-01-UK-en`, `C-CT-01-v1-en`,
    `C-CT-01-v2-en`) — this strips the trailing variant+language segments
    to group sibling rows for the same underlying fact. Not meaningful for
    other families (A/E/F don't use it, and aren't passed through here)."""
    match = _BASE_FACT_ID_RE.match(question_id)
    return match.group("base") if match else None


def _group_siblings(docs: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """`(base_fact_id, language) -> every doc sharing it`, for Set B/C's
    8.3 overlays. Only meaningful within one already-loaded set of docs
    (i.e. one task's own JSONL, already scoped to one language)."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for doc in docs:
        base = _base_fact_id(doc["question_id"])
        if base is None:
            continue
        key = (base, doc.get("language", ""))
        groups.setdefault(key, []).append(doc)
    return groups


def infer_backend(base_url: str) -> str:
    if "11434" in base_url:
        return "ollama"
    if "8081" in base_url or "8080" in base_url or "llamacpp" in base_url:
        return "llamacpp"
    return "unknown"


def fetch_ollama_digest(model_name: str, ollama_url: str = "http://localhost:11434") -> str | None:
    """Query Ollama's own `/api/tags` for `model_name`'s digest directly —
    Ollama runs natively on Windows in this project's setup and, once
    bound to all interfaces (docker-compose.yml's header comment), is
    reachable from plain local Python with no container involved, so
    there's no reason to make the operator run `ollama list` and copy-paste
    a value by hand (5.7/9.6 want a model digest per run; automating its
    collection is more reliable than manual transcription too). Returns
    `None` — not an error — if Ollama isn't reachable or the model isn't
    listed: a digest is a nice-to-have provenance enrichment, not a hard
    requirement to be able to score a run at all.
    """
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(f"{ollama_url}/api/tags", timeout=5) as response:
            data = json.load(response)
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None
    for model in data.get("models", []):
        if model.get("name") == model_name or model.get("model") == model_name:
            return model.get("digest")
    return None


def compute_gguf_digest(gguf_path: Path) -> str | None:
    """SHA256 of the exact GGUF file in use — llama.cpp-served models have
    no Ollama-style digest to query instead, and a computed hash of the
    actual file is more rigorous than a manually-typed value a operator
    might mistype or forget to update after swapping models (5.7/9.6).
    Returns `None` (not an error) if the file doesn't exist — same
    nice-to-have-not-required reasoning as `fetch_ollama_digest`.
    """
    import hashlib

    if not gguf_path.is_file():
        return None
    hasher = hashlib.sha256()
    with open(gguf_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def auto_detect_model_digest(
    model_name: str, backend: str, *, ollama_url: str = "http://localhost:11434", gguf_path: Path | None = None
) -> str | None:
    """Dispatch to whichever automatic digest lookup applies for `backend`
    — the single entry point `scoring.cli` calls so a digest is filled in
    automatically whenever possible, per this project's own "automate as
    much as possible, don't burden the user unnecessarily" principle
    (2026-09-12), rather than defaulting to manual entry.
    """
    if backend == "ollama":
        return fetch_ollama_digest(model_name, ollama_url=ollama_url)
    if backend == "llamacpp":
        return compute_gguf_digest(gguf_path or Path("models/model.gguf"))
    return None


def provenance_from_aggregated_results(
    aggregated_results_path: Path,
    *,
    corpus_version: str,
    model_digest: str | None = None,
    reasoning_mode: str | None = None,
    replicate_index: int | None = None,
) -> RunProvenance:
    """Build a RunProvenance from lm-eval-harness's own aggregated
    `results_*.json` (sibling to the `samples_*.jsonl` file), which carries
    the model name and base_url but not a model digest or which Qwen3
    reasoning-mode condition (ADR 0010) produced the run — neither is
    recorded anywhere in harness output, so both must be supplied
    separately (model digest e.g. from `ollama list`; reasoning_mode is
    simply which condition the operator ran)."""
    with open(aggregated_results_path, encoding="utf-8") as f:
        aggregated = json.load(f)
    model_args = aggregated["config"].get("model_args", {})
    base_url = model_args.get("base_url", "")
    run_timestamp = datetime.fromtimestamp(aggregated["date"], tz=timezone.utc).isoformat()
    return RunProvenance(
        corpus_version=corpus_version,
        model_name=model_args.get("model", aggregated.get("model_name", "unknown")),
        backend=infer_backend(base_url),
        run_timestamp=run_timestamp,
        model_digest=model_digest,
        reasoning_mode=reasoning_mode,
        replicate_index=replicate_index,
    )


# Common-schema (5.6) and family-specific fields worth carrying forward from
# the corpus item into the flat scored row — the analysis layer (Section
# 10) needs these to pair items across languages/varieties/versions
# (`language_variant_of`) and to group by condition, without a separate
# join back to the raw corpus CSV or harness samples file.
_ITEM_CONTEXT_FIELDS = (
    "family", "domain", "language", "variety", "jurisdiction",
    "effective_from", "effective_until", "language_variant_of", "tool_required",
)


@dataclass
class ProvenancedScoredResponse:
    scored: ScoredResponse
    provenance: RunProvenance
    item: dict

    def to_flat_dict(self) -> dict:
        row = {"question_id": self.scored.question_id, "category": self.scored.category.value}
        row["confidence_tier"] = self.scored.confidence_tier.value if self.scored.confidence_tier else None
        row["jurisdiction_adaptation"] = (
            self.scored.jurisdiction_adaptation.value if self.scored.jurisdiction_adaptation else None
        )
        row["currency_awareness"] = (
            self.scored.currency_awareness.value if self.scored.currency_awareness else None
        )
        row["tool_invocation"] = (
            self.scored.tool_invocation.value if self.scored.tool_invocation else None
        )
        row["notes"] = list(self.scored.notes)
        for field_name in _ITEM_CONTEXT_FIELDS:
            row[field_name] = self.item.get(field_name)
        row.update(asdict(self.provenance))
        return row


def score_jsonl_file(jsonl_path: Path, provenance: RunProvenance) -> list[ProvenancedScoredResponse]:
    """Score every sample in one task's `--log_samples` JSONL file.

    One file = one task = one (family, language[, domain/variety]) cell
    (ADR 0009), so sibling grouping for Set B/C overlays is computed once
    per file, from that file's own docs — see module docstring.
    """
    samples = read_samples(jsonl_path)
    docs = [s["doc"] for s in samples]
    family = docs[0]["family"] if docs else None

    sibling_groups = _group_siblings(docs) if family in ("B", "C") else {}

    results = []
    for sample in samples:
        doc = sample["doc"]
        response_text = _raw_response_text(sample)

        siblings = []
        if family in ("B", "C"):
            base = _base_fact_id(doc["question_id"])
            siblings = sibling_groups.get((base, doc.get("language", "")), [])

        scored = score_response(
            question_id=doc["question_id"],
            item=doc,
            response_text=response_text,
            sibling_jurisdiction_items=siblings if family == "B" else None,
            sibling_version_items=siblings if family == "C" else None,
            tool_call_invoked=None,  # not recoverable from generate_until output — see module docstring
        )
        results.append(ProvenancedScoredResponse(scored=scored, provenance=provenance, item=doc))
    return results


def write_scored_jsonl(results: list[ProvenancedScoredResponse], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result.to_flat_dict(), ensure_ascii=False) + "\n")
