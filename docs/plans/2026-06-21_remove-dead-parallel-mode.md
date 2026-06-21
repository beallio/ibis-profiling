# Plan: Remove dead parallel execution mode (finding 2, on trunk) (remove-dead-parallel-mode)

## Context

Code-review finding 2 (re-applied to origin/main): parallel execution is a dead mode.
`_check_parallel_safety()` returns unsafe for every backend (empty allowlist), so `self.parallel`
is always forced `False` and the `ThreadPoolExecutor` branches are unreachable. Delete the dead
mode, keeping only the sequential path that always runs — **behavior-preserving** (today every
profile runs sequentially). Origin's structure matches the session's pre-refactor version exactly.

Relevant files: `src/ibis_profiling/profiler.py` (params, attributes, `_check_parallel_safety`, the
run() safety guard + executor setup, the `finally` shutdown, both `if self.parallel and self.executor: else:`
branches, `profile()` params, the `concurrent.futures` import); `src/ibis_profiling/wrapper.py`
(parallel/pool_size forwarding ~67-68); `README.md` (parallel/pool_size rows if present);
`tests/test_parallel_safety.py` (delete — tests only removed behavior);
`tests/test_histogram_backend_agnostic.py` (rewrite `test_histogram_dict_processing_logic`, which
mocks the parallel branch). `cli.py` does not expose parallel/pool_size; do not touch it.

**Slug used throughout this plan:** `remove-dead-parallel-mode`

---

## Orchestration Contract

**Slug:** `remove-dead-parallel-mode`

**Plan file:**

```text
docs/plans/2026-06-21_remove-dead-parallel-mode.md
```

**Implementation branch:**

```text
feat/remove-dead-parallel-mode
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/remove-dead-parallel-mode_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/remove-dead-parallel-mode_finalized
```

**Review notes:**

```text
docs/review/remove-dead-parallel-mode-review-*.md
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
git checkout -b feat/remove-dead-parallel-mode
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_remove-dead-parallel-mode.md
git commit -m "docs(plan): add remove-dead-parallel-mode implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Behavior-preserving: the sequential path is what already runs.

1. Baseline: `./run.sh uv run pytest -q`.
2. `profiler.py`: remove `from concurrent.futures import ThreadPoolExecutor, as_completed`; remove
   `parallel`/`pool_size` params + `self.parallel`/`self.pool_size`/`self.executor`; delete
   `_check_parallel_safety()`; delete the run() "Parallel Safety Guard" block (the
   `_check_parallel_safety` call, `self.parallel = False`, the `ThreadPoolExecutor` setup, and any
   "Parallel mode disabled" warning); remove the `finally` `executor.shutdown` block (keep
   `return report` reachable); collapse the histogram branch to `results = [run_hist(p) for p in histogram_plans]`
   and the table-metrics branch to `results = [run_table_plan(p) for p in table_plans]`; remove
   `parallel`/`pool_size` from `profile()` and its `Profiler(...)` call.
3. `wrapper.py`: remove the `parallel=`/`pool_size=` forwarding.
4. `README.md`: delete the `parallel`/`pool_size` option rows if present.
5. Delete `tests/test_parallel_safety.py`.
6. Rewrite `tests/test_histogram_backend_agnostic.py::test_histogram_dict_processing_logic` to drive
   the real sequential path (no `as_completed`/executor mocking): on a DuckDB-backed memtable, call
   `_run_advanced_pass(report)` with `report` a `MagicMock(spec=InternalProfileReport)`, and assert a
   `numeric_histogram` metric is added for the column with a non-empty `counts` list. Keep
   `test_histogram_duckdb_backend` unchanged.

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

1. `scripts/orchestration/run-quality-gates` passes — regression gate at 0 differences (behavior-preserving).
2. `grep -rnE "parallel|pool_size|ThreadPool|as_completed|_check_parallel_safety|self.executor" src tests README.md`
   returns no matches (ignore vendored JS).
3. `tests/test_parallel_safety.py` no longer exists; `ruff check .` shows no unused imports.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished remove-dead-parallel-mode
```

This writes:

```text
/tmp/ibis-profiling/remove-dead-parallel-mode_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer remove-dead-parallel-mode`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/remove-dead-parallel-mode-review-*.md
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
   scripts/orchestration/clear-finished remove-dead-parallel-mode
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
   git add docs/review/remove-dead-parallel-mode-review-*.md
   git commit -m "docs(review): record remove-dead-parallel-mode review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished remove-dead-parallel-mode
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer remove-dead-parallel-mode` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed remove-dead-parallel-mode
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize remove-dead-parallel-mode
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/remove-dead-parallel-mode_finalized
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
scripts/orchestration/finalize remove-dead-parallel-mode
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/remove-dead-parallel-mode_finished
/tmp/ibis-profiling/remove-dead-parallel-mode_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
