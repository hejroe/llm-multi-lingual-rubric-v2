"""Language-aware marker detection (8.6) and the invented-detail heuristic (8.7).

IDK markers are looked up per language from `data/idk_markers.json`, a
machine-readable copy of Appendix A.3 — not an English list applied
everywhere (8.6).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from scoring.matching import normalise_for_matching, strip_think_blocks

_DATA_DIR = Path(__file__).parent / "data"


def _load_idk_markers() -> dict[str, list[str]]:
    with open(_DATA_DIR / "idk_markers.json", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


_IDK_MARKERS = _load_idk_markers()


def idk_marker_present(response_text: str, language: str) -> bool:
    """Does an IDK marker for `language` appear in the response?

    Falls back to the English list if `language` has no maintained list yet,
    rather than silently reporting no marker could ever fire for it — but a
    missing per-language list is itself worth surfacing, not hidden (12.1
    style: state the limitation, don't paper over it).
    """
    markers = _IDK_MARKERS.get(language, _IDK_MARKERS["en"])
    normalised_response = normalise_for_matching(response_text)
    return any(
        normalise_for_matching(marker) in normalised_response for marker in markers
    )


# --- 8.4 step 4: IDK vs. a hedge-accompanied wrong answer -------------------

# Rough per-language filler the hedge leaves behind once the marker itself is
# removed (connectives, articles) — used only to judge whether *anything*
# beyond boilerplate remains, not to extract or judge the remaining content.
_FILLER_WORDS = {
    "en": {
        "but",
        "though",
        "however",
        "maybe",
        "perhaps",
        "possibly",
        "something",
        "about",
        "with",
        "to",
        "do",
        "i",
        "think",
        "it",
        "the",
        "a",
        "an",
        "of",
        "is",
        "are",
    },
}


def has_definite_stated_answer(response_text: str, language: str) -> tuple[bool, bool]:
    """Classify the non-hedge remainder of a response carrying an IDK marker.

    Returns `(is_definite, is_ambiguous)`:
    - `(True, False)`  — a clear, specific alternative answer is stated
      alongside the hedge (RUBRIC_CARDS.md's Golgi-apparatus example): not
      IDK, proceed to step 6, High-Confidence.
    - `(False, False)` — nothing beyond the hedge itself: IDK,
      High-Confidence.
    - `(False, True)`  — a partial, non-specific attempt alongside the hedge
      (the "possibly something to do with energy production" example): the
      genuinely ambiguous middle case (8.7) — tag Heuristic-Guidance,
      wherever it lands.

    "Definite" is explicitly a graded judgement, not a binary test (8.7) —
    this heuristic distinguishes specific content (proper nouns, numbers, or
    a reasonably long remainder) from filler, it does not parse meaning.
    """
    markers = _IDK_MARKERS.get(language, _IDK_MARKERS["en"])
    remainder = normalise_for_matching(response_text)
    for marker in markers:
        remainder = remainder.replace(normalise_for_matching(marker), " ")

    filler = _FILLER_WORDS.get(language, _FILLER_WORDS["en"])
    remaining_words = [w for w in remainder.split() if w not in filler]

    if not remaining_words:
        return False, False

    has_digit = any(any(ch.isdigit() for ch in w) for w in remaining_words)
    if has_digit or len(remaining_words) >= 3:
        return True, False

    # Some non-filler content, but short and generic (e.g. "energy
    # production") — the genuinely ambiguous middle case.
    return False, True


# --- 8.4 step 6: Incorrect-Guess vs. Fabrication ----------------------------

_YEAR_RE = re.compile(r"\b(1[5-9]\d{2}|20\d{2})\b")
_PROPER_NOUN_RUN_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")
_CITATION_HINT_RE = re.compile(
    r"\baccording to\b|\bet al\.?\b|\bpublished in\b|\bstudy by\b", re.IGNORECASE
)


# Languages where a run of capitalised words is a meaningful signal of a
# specific proper noun, as opposed to ordinary capitalisation grammar (German
# capitalises every noun, common or proper, which would otherwise make this
# heuristic fire on plain wrong answers like "Der Zellkern" — an
# English-centric assumption baked into a supposedly language-aware
# heuristic, exactly the kind of bug 8.5 exists to avoid; excluded here
# rather than silently mismeasured).
_PROPER_NOUN_HEURISTIC_LANGUAGES = {"en", "sw"}


def invented_detail_signal(
    response_text: str, question_text: str, language: str = "en"
) -> tuple[bool, bool]:
    """Look for invented specifics (names, dates, citations) not present in
    the question (8.2's Fabrication definition).

    Returns `(found_invented_detail, is_clear_cut)`. `is_clear_cut=False`
    signals a borderline/weak case (8.7's Heuristic-Guidance path) rather
    than a confident finding either way.
    """
    stripped = strip_think_blocks(response_text)
    question_norm = normalise_for_matching(question_text)

    years_found = [y for y in _YEAR_RE.findall(stripped) if y not in question_norm]
    proper_noun_runs = []
    if language in _PROPER_NOUN_HEURISTIC_LANGUAGES:
        proper_noun_runs = [
            m
            for m in _PROPER_NOUN_RUN_RE.findall(stripped)
            if normalise_for_matching(m) not in question_norm
        ]
    has_citation_hint = bool(_CITATION_HINT_RE.search(stripped))

    # Clear-cut: a specific year or multi-word proper-noun run not in the
    # question, especially paired with a citation-style hint (the
    # "Camillo Golgi... 1898 paper" worked example).
    if (years_found or proper_noun_runs) and (
        has_citation_hint or (years_found and proper_noun_runs)
    ):
        return True, True

    if years_found or proper_noun_runs or has_citation_hint:
        # Some signal, but not the compounded pattern above — borderline.
        return True, False

    return False, True
