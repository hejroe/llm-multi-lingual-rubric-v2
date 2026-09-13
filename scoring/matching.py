"""Text normalisation and gold-answer matching (8.4 steps 2-3).

Each function here fixes one of the three scoring-pipeline bugs the original
review found (8.5): think-block leakage, English-only matching, and (via
normalisation) the accent/variety sensitivity that made otherwise-correct
non-English or non-US-spelling answers register as wrong.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)

_PUNCTUATION_RE = re.compile(r"[.,;:!?'\"()\[\]{}]")
_WHITESPACE_RE = re.compile(r"\s+")


def strip_think_blocks(text: str) -> str:
    """8.4 step 2: remove reasoning/chain-of-thought blocks before matching.

    Prevents the original repo's bug where an unstripped `<think>` block was
    scored as if it were the final answer (8.5).
    """
    return _THINK_BLOCK_RE.sub("", text)


def extract_think_blocks(text: str) -> tuple[str, str | None]:
    """Same stripping as `strip_think_blocks`, but also returns whatever was
    removed (`None` if there was nothing to remove) — added (2026-09-12,
    ADR 0010) so a reasoning trace is preserved as part of the scored
    record for audit (Section 11) rather than simply discarded once used
    for matching. This only recovers a trace embedded in `content` behind
    `<think>` tags; a backend that returns reasoning in a genuinely
    separate API field (llama.cpp's `reasoning_content`, confirmed
    2026-09-12) is not captured here at all — stock lm-eval-harness's own
    response parsing discards that field before `--log_samples` ever sees
    it, a capture gap this function cannot close (see scoring/io.py's
    module docstring).
    """
    matches = _THINK_BLOCK_RE.findall(text)
    reasoning_trace = "\n".join(matches) if matches else None
    return _THINK_BLOCK_RE.sub("", text), reasoning_trace


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _load_variety_conversion() -> dict:
    with open(_DATA_DIR / "variety_conversion.json", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


_VARIETY_CONVERSION = _load_variety_conversion()


def normalise_for_matching(text: str) -> str:
    """Case-fold, strip accents/punctuation, and collapse whitespace.

    Language-agnostic by design (5.6/6.3): this is what makes matching
    language- and variety-appropriate rather than the original repo's
    English-only regex (8.5).
    """
    text = text.strip().lower()
    text = _strip_accents(text)
    text = _PUNCTUATION_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def _variety_equivalents(word: str) -> set[str]:
    """All known spellings of `word` across the tracked US/UK/AU variants."""
    equivalents = {word}
    for table in _VARIETY_CONVERSION.values():
        for us_word, variant_word in table.items():
            if word in (us_word, variant_word):
                equivalents.add(us_word)
                equivalents.add(variant_word)
    return equivalents


_ARITHMETIC_WORKING_RE = re.compile(r"\d+\s*[+\-−*×x/÷]\s*\d+\s*=")


def shows_arithmetic_working(response_text: str) -> bool:
    """A crude proxy for "a method was shown" (8.4 step 5, Correct-Process):
    at least one `number operator number =` pattern, i.e. more than just a
    bare final answer. Says nothing about whether the method is valid."""
    return bool(_ARITHMETIC_WORKING_RE.search(response_text))


_NUMERIC_GOLD_RE = re.compile(r"^\d+%?$")


def _contains_whole(haystack: str, needle: str) -> bool:
    """Word-boundary-aware substring test: `needle` must not be embedded
    inside a larger alphanumeric token in `haystack`. Checks the actual
    characters adjacent to each candidate match, rather than regex `\\b`
    (which fails whenever `needle` itself ends in a non-word character,
    e.g. a percentage sign — `\\b` requires a word/non-word *transition*,
    and neither side of "...25%" + end-of-string is a word character, so
    `\\b` after `%` never matches at all — found via a real test failure,
    2026-09-13, using exactly this shape of gold answer).
    """
    if not needle:
        return False
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            return False
        before_ok = idx == 0 or not haystack[idx - 1].isalnum()
        end = idx + len(needle)
        after_ok = end == len(haystack) or not haystack[end].isalnum()
        if before_ok and after_ok:
            return True
        start = idx + 1


def matches_gold_answer(response_text: str, gold_answer: str) -> bool:
    """8.4 step 3: does the (already think-stripped) response contain the
    gold answer, under accent-insensitive, variety-aware matching?

    Purely numeric gold answers (an age, a rate — Sets B/C's item shape
    throughout) use a word-boundary-aware test (`_contains_whole`):
    found necessary 2026-09-13, a plain `in` substring test made any
    numeric gold answer a false-positive magnet ("18" matched inside
    "1800s" or "218 dollars"). Everything else keeps a plain substring
    test deliberately, including the variety-equivalents check below: a
    Set F item's "wrong" variety spelling for a tracked word (Appendix
    A.2) needs to match inside an inflected form too (e.g. "colour"
    inside "coloured"/"colours"), which a whole-word test would reject
    (RUBRIC_CARDS.md's "Correct" card, common confusion) — the
    false-positive risk profile for a handful of common whole words is not
    the same as for short numeric strings, which are far more likely to
    appear embedded inside an unrelated larger number.
    """
    if not gold_answer:
        # Set B's unspecified-jurisdiction variant carries no gold_answer
        # (5.6) — Correct is simply not assessed for it.
        return False

    normalised_response = normalise_for_matching(response_text)
    normalised_gold = normalise_for_matching(gold_answer)
    is_numeric = bool(_NUMERIC_GOLD_RE.match(normalised_gold))

    if is_numeric:
        if _contains_whole(normalised_response, normalised_gold):
            return True
    elif normalised_gold in normalised_response:
        return True

    for variant in _variety_equivalents(normalised_gold):
        if variant == normalised_gold:
            continue  # already checked above; a numeric gold has no variants anyway
        if variant in normalised_response:
            return True

    return False
