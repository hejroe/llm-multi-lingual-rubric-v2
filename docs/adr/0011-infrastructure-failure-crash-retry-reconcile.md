# 0011. Infrastructure-Failure detection via whole-run retry and post-hoc reconciliation

**Status:** Accepted
**Date:** 2026-09-12

## Context

Protocol 8.2/9.3 require a persistently-failing request to be tagged
Infrastructure-Failure and continue, not silently drop the item or crash
the whole run. Stock `lm-evaluation-harness`, however, has no mechanism
to do this: `local-chat-completions`'s per-request retry
(`lm_eval/models/api_models.py`) either succeeds silently or, once
`max_retries` is exhausted, raises an exception that crashes the *entire*
run — every item still queued is lost, not just the one that failed.
Reimplementing the harness's internal retry-then-reraise logic
(`generate_until`) directly was considered and rejected: it would couple
this project to private implementation details of an upstream dependency
likely to change on any version bump, undermining the reproducibility the
Dockerfile's own digest-pinning (9.7) exists to guarantee.

## Decision

Wrap `lm_eval` in `scripts/robust_run.py` rather than patching it:

1. Retry the *whole* `lm_eval` invocation on a crash (up to
   `--run-retries`, default 3), using the harness's own public
   `--use_cache` flag so already-completed items are never redundantly
   re-queried on a retry.
2. Once retries are exhausted (or immediately, if the run succeeded),
   reconcile the actual output against the task's full expected item set
   — rebuilt the same way the harness itself would, via its own
   `_yaml_loader` and `datasets.load_dataset`, not a hand-maintained
   parallel mapping that could drift out of sync — and write anything
   that never got a response as an explicit empty-response stub row to a
   separate `*.missing.jsonl`, never mutating the harness's own raw
   samples file (Protocol 5.7).
3. `scoring/rubric.py`'s existing empty-response check already tags an
   empty response Infrastructure-Failure — no separate marker or
   scoring-side change is needed for the reconciled stub rows.

## Consequences

- Every real run goes through `robust_run.py`, never `lm_eval` directly
  (`scripts/README.md`).
- Verified live (2026-09-12) against both a genuine transient-style
  failure and a deliberate total-connection-failure case; that same
  testing caught two real bugs, both fixed before this became the
  default path: `--limit` being ignored during reconciliation (every
  un-scheduled item wrongly flagged missing) and a crash so early that no
  output directory existed at all being wrongly reported as "recovered."
- Not yet independently exercised against a genuinely intermittent
  failure (some items succeed, one specific item times out) — every test
  so far has been either "every item succeeds" or "every item fails,"
  since that's what's straightforward to induce deliberately.
- This design decision was not recorded here until 2026-09-13, despite
  being comparable in weight to ADR 0008/0009 (a core Protocol
  commitment — 8.2/9.3's Infrastructure-Failure category — realized via a
  specific, non-obvious mechanism with rejected alternatives) — found
  during review to be documented only in the module's own docstring.
  Recorded now so a reviewer can find the *why* here rather than only in
  code.
