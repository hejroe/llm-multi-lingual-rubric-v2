"""Operational wrappers around `lm_eval` itself (robust_run.py,
replicate_run.py) — as opposed to `scoring/` and `analysis/`, which run
after the harness has already produced output. A package only so that
`python -m scripts.replicate_run` can import `scripts.robust_run` reliably
(see replicate_run.py's own docstring for why direct file invocation
doesn't work).
"""
