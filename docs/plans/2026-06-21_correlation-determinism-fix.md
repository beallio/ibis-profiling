# Plan: Seed correlation/interaction sampling for determinism (on trunk) (correlation-determinism-fix)

## Context

Newly-found determinism issue (re-applied to origin/main): profiling the same table twice yields
different `correlations` and `interactions` because both sample via an unseeded `table.sample()`
(`correlations.py:84`, `interactions.py:71`). Fix: thread a defaulted `sample_seed` through
`profile()`/`Profiler`/`ProfileConfig` into both `table.sample(..., seed=sample_seed)` calls so a
given `(table, config, seed)` yields identical output.

Note: this trunk already has the typed `ProfileConfig` (from finding 1), so `sample_seed` must be a
`ProfileConfig` field too. The regression gate excludes correlations/interactions on this trunk, so
it stays at 0 differences (seeding only changes those excluded sections); the new determinism test
is the oracle for the fix. (Re-including correlations in the gate is a deferred follow-up.)

Relevant files: `src/ibis_profiling/config.py` (add `sample_seed` field + to `resolve`);
`src/ibis_profiling/profiler.py` (`sample_seed: int = 42` param on `Profiler.__init__` and
`profile()`; pass `self.config.sample_seed` to the correlation + interaction engines);
`src/ibis_profiling/report/model/correlations.py` + `interactions.py` (add `sample_seed: int | None
= None`, seed the `table.sample`); NEW `tests/test_correlation_determinism.py`.

**Slug used throughout this plan:** `correlation-determinism-fix`

---

## Orchestration Contract

**Slug:** `correlation-determinism-fix`

**Plan file:**

```text
docs/plans/2026-06-21_correlation-determinism-fix.md
```

**Implementation branch:**

```text
feat/correlation-determinism-fix
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/correlation-determinism-fix_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/correlation-determinism-fix_finalized
```

**Review notes:**

```text
docs/review/correlation-determinism-fix-review-*.md
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
3. Branch from `refactor/findings-on-trunk`.
4. Commit this plan as the first commit on the implementation branch.
5. Follow TDD where behavior changes are testable.
6. Run quality gates before marking any round complete.
7. Do not write your own review.
8. Do not create files under `docs/review/`.
9. Do not delete files under `docs/review/`.
10. Review notes are durable audit records and must be committed.
11. Resolving a review note means:
    - implement the requested changes;
    - run quality gates;
    - commit the code/docs changes;
    - commit the review note itself if it is not already committed;
    - recreate the round-complete marker.
12. After finalization, stop polling and exit cleanly.

---

## Setup

Start from `refactor/findings-on-trunk`:

```bash
git checkout refactor/findings-on-trunk
# ORCH_LOCAL_ONLY: local trial branch, skipping origin pull
git checkout -b feat/correlation-determinism-fix
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_correlation-determinism-fix.md
git commit -m "docs(plan): add correlation-determinism-fix implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. TDD: write the determinism test first (RED today — sampling is unseeded).

1. Baseline: `./run.sh uv run pytest -q`.
2. `tests/test_correlation_determinism.py` FIRST: build a ~5,000-row `ibis.memtable` with a few
   numeric columns; profile twice with sampling forced on + a fixed seed
   (`profile(t, correlations_sampling_threshold=10, correlations_sample_size=200, sample_seed=7)`)
   and assert the `correlations` (pearson+spearman matrices) and `interactions` sections are EQUAL;
   profile once more with a different `sample_seed` and assert the correlation matrices DIFFER.
3. Add `sample_seed: int = 42` to `Profiler.__init__` and `profile()`; add a `sample_seed` field to
   `ProfileConfig` (default 42) and to `ProfileConfig.resolve(...)`; store `self.sample_seed =
   self.config.sample_seed`.
4. `correlations.py::CorrelationEngine.compute_all`: add `sample_seed: int | None = None`; change
   `table.sample(sample_fraction)` -> `table.sample(sample_fraction, seed=sample_seed)`.
   `interactions.py::InteractionEngine.compute`: add `sample_seed: int | None = None`; seed its
   `table.sample(...)`. In `profiler.py`, pass `sample_seed=self.config.sample_seed` to both calls.
   Keep the `except Exception: ... limit(...)` fallbacks.
5. Confirm `./run.sh uv run pytest tests/test_correlation_determinism.py` passes.

---

## Quality Gates

Run before marking any round complete:

```bash
scripts/orchestration/run-quality-gates
scripts/orchestration/check-review-notes-not-deleted
git status --short
```

The round is not complete unless:

1. all requested implementation work is done;
2. all relevant tests pass;
3. build/typecheck gates pass;
4. review notes have not been deleted;
5. the working tree is clean;
6. all code/docs changes are committed.

---

## Verification

1. `scripts/orchestration/run-quality-gates` passes — regression gate 0 differences (the gate
   excludes correlations/interactions, so the non-correlation surface is unchanged).
2. The determinism test passes (same seed identical; different seed differs).
3. `grep -n "seed" src/ibis_profiling/report/model/correlations.py src/ibis_profiling/report/model/interactions.py`
   shows the seed threaded into both `table.sample(...)`. `ty check src/` + `ruff` clean.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished correlation-determinism-fix
```

This writes:

```text
/tmp/ibis-profiling/correlation-determinism-fix_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer correlation-determinism-fix`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/correlation-determinism-fix-review-*.md
```

When a review note exists or a new review note appears:

1. Read the full review note.
2. If the note ends with:

   ```text
   STATUS: CHANGES_REQUESTED
   ```

   then resume work.

3. Clear the round-complete marker:

   ```bash
   scripts/orchestration/clear-finished correlation-determinism-fix
   ```

4. Address every requested change.
5. Run quality gates:

   ```bash
   scripts/orchestration/run-quality-gates
   scripts/orchestration/check-review-notes-not-deleted
   ```

6. Commit code/docs fixes.
7. Commit the review-note file itself if it is not already committed:

   ```bash
   git add docs/review/correlation-determinism-fix-review-*.md
   git commit -m "docs(review): record correlation-determinism-fix review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished correlation-determinism-fix
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer correlation-determinism-fix` after the next review note is created.

---

## Approval Handling

If the latest review note ends with:

```text
STATUS: APPROVED
```

then:

1. Confirm every previous review item has been addressed.
2. Confirm all review notes are committed:

   ```bash
   scripts/orchestration/check-review-notes-committed correlation-determinism-fix
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize correlation-determinism-fix
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/correlation-determinism-fix_finalized
   ```

6. Stop polling and exit cleanly.

---

## Review Rules

Do not write your own review.

Do not create files under:

```text
docs/review/
```

Do not delete files under:

```text
docs/review/
```

Only the orchestrator writes review notes. Your job is to read them, resolve them, commit them as audit records, and continue the loop.

---

## Finalization Rules

Only finalize after a review note with:

```text
STATUS: APPROVED
```

Finalization is performed with:

```bash
scripts/orchestration/finalize correlation-determinism-fix
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/correlation-determinism-fix_finished
/tmp/ibis-profiling/correlation-determinism-fix_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
