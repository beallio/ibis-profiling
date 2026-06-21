# Plan: Remove dead BackendAdapter indirection (finding 8, on trunk) (engine-adapter-cleanup)

## Context

Code-review finding 8 (re-applied to origin/main): the backend adapter layer in
`src/ibis_profiling/engine.py` is an abstraction with no behavior. `BackendAdapter` (Protocol),
`DuckDBAdapter`, `DefaultAdapter`, the `ExecutionEngine._adapters` registry, and
`ExecutionEngine._get_adapter()` exist solely to return `None` from `get_storage_size()`.

Intended outcome: delete the dead adapter indirection while preserving behavior.
`ExecutionEngine.execute()` is real and used — keep it unchanged. `ExecutionEngine.get_storage_size(table)`
must remain and keep returning `None` (every existing test asserts `None`), but directly.

Relevant files: `src/ibis_profiling/engine.py` (only production change). Callers/tests that assert
`get_storage_size(...) is None`: `tests/test_engine.py`, `tests/test_coverage_gap_closure.py`,
`tests/test_security_integration.py`, `tests/test_security_fixes.py` — must still pass unchanged.
`src/ibis_profiling/profiler.py` falls back to `DatasetInspector.estimate_memory_size()`; do not
change profiler behavior.

**Slug used throughout this plan:** `engine-adapter-cleanup`

---

## Orchestration Contract

**Slug:** `engine-adapter-cleanup`

**Plan file:**

```text
docs/plans/2026-06-21_engine-adapter-cleanup.md
```

**Implementation branch:**

```text
feat/engine-adapter-cleanup
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/engine-adapter-cleanup_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/engine-adapter-cleanup_finalized
```

**Review notes:**

```text
docs/review/engine-adapter-cleanup-review-*.md
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
git checkout -b feat/engine-adapter-cleanup
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_engine-adapter-cleanup.md
git commit -m "docs(plan): add engine-adapter-cleanup implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Baseline: `./run.sh uv run pytest tests/test_engine.py tests/test_coverage_gap_closure.py tests/test_security_integration.py tests/test_security_fixes.py -q` (these assert `get_storage_size(...) is None`).
2. Edit `src/ibis_profiling/engine.py`:
   - Delete `BackendAdapter`, `DuckDBAdapter`, `DefaultAdapter`, `ExecutionEngine.__init__` (the `_adapters` registry), and `ExecutionEngine._get_adapter()`.
   - Replace `ExecutionEngine.get_storage_size()` with a direct `return None` (keep the exact
     signature `def get_storage_size(self, table: ibis.Table) -> int | None:`), with a short
     docstring that backend-specific sizing is not implemented.
   - Keep `ExecutionEngine.execute()` exactly as-is.
   - Remove now-unused imports (`logging`, `Protocol`, `IbisError`); keep `ibis`, `ir`, `pl`, `cast`.
3. Do not change any test assertions; the tests construct `ExecutionEngine()` and assert `None`.

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

1. `scripts/orchestration/run-quality-gates` passes — including the regression gate at 0 differences
   (behavior-preserving) and the four storage-size tests.
2. `grep -rn "BackendAdapter\|DuckDBAdapter\|DefaultAdapter\|_get_adapter\|_adapters" src tests` returns nothing.
3. `ruff check .` reports no unused imports in `engine.py`.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished engine-adapter-cleanup
```

This writes:

```text
/tmp/ibis-profiling/engine-adapter-cleanup_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer engine-adapter-cleanup`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/engine-adapter-cleanup-review-*.md
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
   scripts/orchestration/clear-finished engine-adapter-cleanup
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
   git add docs/review/engine-adapter-cleanup-review-*.md
   git commit -m "docs(review): record engine-adapter-cleanup review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished engine-adapter-cleanup
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer engine-adapter-cleanup` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed engine-adapter-cleanup
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize engine-adapter-cleanup
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/engine-adapter-cleanup_finalized
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
scripts/orchestration/finalize engine-adapter-cleanup
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/engine-adapter-cleanup_finished
/tmp/ibis-profiling/engine-adapter-cleanup_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
