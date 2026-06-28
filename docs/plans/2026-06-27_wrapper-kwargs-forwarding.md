# Plan: Fix silent kwarg drops and unify forwarding in the ProfileReport wrapper (finding 1) (wrapper-kwargs-forwarding)

## Context

Thermo-nuclear review finding 1 (main, commit `d2b589d`). `ProfileConfig.resolve()` is already the
single canonical place that resolves defaults/validation, so the "config split across surfaces"
framing is overstated — but the review surfaces a **real, narrow bug**: the `ProfileReport`
compatibility wrapper accepts `**kwargs` and forwards only a hand-picked subset to `profile()`.

Concretely, `profile()` supports `sample_seed` and `inference_sample_size`
(`src/ibis_profiling/profiler.py:726`, `:733`), and both are real `ProfileConfig` fields
(`src/ibis_profiling/config.py:18`, `:25`). But the wrapper's `profile()` call
(`src/ibis_profiling/wrapper.py:46-69`) never forwards them. So:

```python
ProfileReport(table, sample_seed=7)          # swallowed into self.kwargs, ignored
ProfileReport(table, inference_sample_size=0) # swallowed, ignored
ProfileReport(table, typformo=1)             # typo also silently swallowed
```

The value lands in `self.kwargs` and is silently dropped. Any other unknown kwarg (including typos
of real option names) is also accepted with no signal. This is a forwarding-completeness gap plus a
silent-failure footgun, not a structural rewrite. Scope is intentionally small and behavior is
additive: previously-dropped options start taking effect, and genuinely unknown kwargs start
warning.

Relevant files:
- `src/ibis_profiling/wrapper.py` (forward `sample_seed`/`inference_sample_size`; warn on unknown
  kwargs).
- `tests/` (new focused forwarding test; see Implementation Tasks).
- `README.md` only if it documents the wrapper's accepted options (verify before editing).

Out of scope (the review's larger "one typed options object shared by `profile()`/`Profiler`/
`ProfileReport`/`from_excel`/CLI" suggestion): `ProfileConfig.resolve()` already owns resolution;
collapsing the thin parameter-passing at each public boundary is a separate, behavior-neutral
refactor that can follow later if desired. This round fixes the bug only.

**Slug used throughout this plan:** `wrapper-kwargs-forwarding`

---

## Orchestration Contract

**Slug:** `wrapper-kwargs-forwarding`

**Plan file:**

```text
docs/plans/2026-06-27_wrapper-kwargs-forwarding.md
```

**Implementation branch:**

```text
feat/wrapper-kwargs-forwarding
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/wrapper-kwargs-forwarding_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/wrapper-kwargs-forwarding_finalized
```

**Review notes:**

```text
docs/review/wrapper-kwargs-forwarding-review-*.md
```

Each review note ends with exactly one status trailer:

```text
STATUS: CHANGES_REQUESTED
```

or:

```text
STATUS: APPROVED
```

---

## Required Agent Protocol

1. Use the **implementer** skill.
2. Work from the repository root.
3. Branch from `dev`.
4. Commit this plan as the first commit on the implementation branch.
5. Follow TDD where behavior changes are testable.
6. Run quality gates before marking any round complete.
7. Do not write your own review.
8. Do not create files under `docs/review/`.
9. Do not delete files under `docs/review/`.
10. Review notes are durable audit records and must be committed.
11. Resolving a review note means: implement the requested changes; run quality gates; commit the
    code/docs changes; commit the review note itself if not already committed; recreate the
    round-complete marker.
12. After finalization, stop polling and exit cleanly.

---

## Setup

```bash
git checkout dev
git pull --ff-only
git checkout -b feat/wrapper-kwargs-forwarding
git add docs/plans/2026-06-27_wrapper-kwargs-forwarding.md
git commit -m "docs(plan): add wrapper-kwargs-forwarding implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. TDD: write the forwarding tests first.

1. Baseline: `./run.sh uv run pytest -q`.
2. Add a focused forwarding test (e.g. `tests/test_wrapper_forwarding.py`) that asserts every
   public `profile()` option reaches `profile()` through `ProfileReport`. Monkeypatch/spy on
   `ibis_profiling.wrapper.profile` to capture the kwargs it is called with, then construct
   `ProfileReport(table, <option>=<sentinel>)` for each forwardable option and assert the sentinel
   arrives. Cover at minimum the two currently-dropped ones: `sample_seed` and
   `inference_sample_size`. Also assert that the already-forwarded `kwargs.get(...)` options
   (`cardinality_threshold`, `max_interaction_pairs`, `correlations_sampling_threshold`,
   `correlations_sample_size`, `use_sketches`) still arrive — guard against regressions while
   editing the call site.
3. Add a test asserting an unknown kwarg (e.g. `ProfileReport(table, definitely_not_an_option=1)`)
   raises `warnings.warn` (use `pytest.warns`). Keep `title` exempt (it is a legitimate display
   kwarg the wrapper consumes directly).
4. Fix `src/ibis_profiling/wrapper.py`:
   - Forward `sample_seed` and `inference_sample_size` to the `profile()` call. Mirror the existing
     `kwargs.get("<name>", <default>)` style and use the same defaults `profile()` declares
     (`sample_seed=42`, `inference_sample_size=10_000`) so behavior is unchanged when the caller
     omits them.
   - After consuming known kwargs, detect leftover unknown keys and `warnings.warn(...)` (do not
     raise — this is a compatibility shim and raising would break lenient ydata-style callers).
     Build the "known kwarg names" set from the keys the wrapper actually reads plus `title`, so
     adding a future option in one place keeps the warning accurate.
5. Confirm `inference_sample_size` plumbs end-to-end: `Profiler` -> `ProfileConfig.resolve` ->
   logical-type inference. (`profile()` already accepts it; this only needs the wrapper to forward.)
6. If `README.md` documents the wrapper's option list, add the two now-forwarded options; otherwise
   leave docs untouched.

---

## Quality Gates

Run before marking any round complete:

```bash
scripts/orchestration/run-quality-gates
scripts/orchestration/check-review-notes-not-deleted
git status --short
```

The round is not complete unless: all work is done; relevant tests pass; build/typecheck gates
pass; review notes are not deleted; the working tree is clean; all changes are committed.

---

## Verification

1. `./run.sh uv run pytest -q` passes, including the new forwarding tests.
2. `ProfileReport(table, sample_seed=7)` results in `profile()` receiving `sample_seed=7`
   (covered by the spy test).
3. `ProfileReport(table, inference_sample_size=N)` reaches logical-type inference (the
   forwarding test asserts the kwarg arrives at `profile()`).
4. An unknown kwarg triggers a `UserWarning` (covered by `pytest.warns`).
5. No behavior change when callers pass none of the newly-forwarded options (defaults match
   `profile()`).
6. The regression baseline is unaffected (the wrapper isn't on the gate path); if the gate runs,
   it shows 0 diffs.

---

## Mark Round Complete

```bash
scripts/orchestration/mark-finished wrapper-kwargs-forwarding
```

Then exit cleanly. If the process exits, the orchestrator resumes you via
`scripts/orchestration/continue-implementer wrapper-kwargs-forwarding`.

---

## Review Polling Loop

After marking complete, check existing review notes, then poll for new ones at
`docs/review/wrapper-kwargs-forwarding-review-*.md`. When a note exists:

1. Read the full note.
2. If it ends with `STATUS: CHANGES_REQUESTED`, resume work.
3. Clear the marker: `scripts/orchestration/clear-finished wrapper-kwargs-forwarding`.
4. Address every requested change.
5. Run quality gates (`run-quality-gates`, `check-review-notes-not-deleted`).
6. Commit code/docs fixes.
7. Commit the review-note file if not already committed:
   `git add docs/review/wrapper-kwargs-forwarding-review-*.md && git commit -m "docs(review): record wrapper-kwargs-forwarding review notes"`.
8. Recreate the marker: `scripts/orchestration/mark-finished wrapper-kwargs-forwarding`.
9. Continue polling or exit cleanly.

---

## Approval Handling

If the latest review note ends with `STATUS: APPROVED`:

1. Confirm every prior item is addressed.
2. `scripts/orchestration/check-review-notes-committed wrapper-kwargs-forwarding`.
3. `git status --short` (clean).
4. `scripts/orchestration/finalize wrapper-kwargs-forwarding`.
5. Confirm `/tmp/ibis-profiling/wrapper-kwargs-forwarding_finalized` exists.
6. Stop polling and exit cleanly.

---

## Review Rules

Do not write your own review. Do not create or delete files under `docs/review/`. Only the
orchestrator writes review notes; you read, resolve, and commit them as audit records.

---

## Finalization Rules

Only finalize after a `STATUS: APPROVED` note, via
`scripts/orchestration/finalize wrapper-kwargs-forwarding`. Do not manually merge into `dev`
unless finalize fails and you are explicitly told to recover manually. Leave both markers in place
after finalization.
