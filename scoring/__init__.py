"""Rubric-based scoring of raw lm-eval-harness output (STUDY_PROTOCOL.md
Section 8): matches responses against gold answers, applies the category/
confidence-tier decision logic, and attaches run provenance. Stdlib-only
by design (Section 6) — no scipy/numpy dependency here; that lives in
`analysis/` instead, which consumes this package's scored JSONL output.
"""
