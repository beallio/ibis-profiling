# Plan: Fix pytest collecting from scripts/ (finding 6.1, on trunk) (test-collection-boundary)

## Context

Code-review finding 6 (increment 6.1, re-applied to origin/main): `pytest` collects ad-hoc
`scripts/test_*.py` exploratory scripts alongside the real suite. Establish a clean test boundary:
relocate the 3 genuine test modules into `tests/`, and scope collection to `tests/` so the
remaining manual scripts are ignored.

Genuine tests (have `def test_` functions) -> move to `tests/`: `scripts/test_ibis_batching.py`,
`scripts/test_nunique_nulls.py`, `scripts/test_window_batching.py`. Manual scripts (no test
functions, keep in `scripts/`, no longer collected): `scripts/test_financial_data.py`,
`scripts/test_report_gen.py`.

Relevant files: those scripts; `pyproject.toml` (`[tool.pytest.ini_options]` — add
`testpaths = ["tests"]`, ensure `pythonpath = ["src", "."]`).

**Slug used throughout this plan:** `test-collection-boundary`

---

## Orchestration Contract

**Slug:** `test-collection-boundary`

**Plan file:**

```text
docs/plans/2026-06-21_test-collection-boundary.md
```

**Implementation branch:**

```text
feat/test-collection-boundary
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/test-collection-boundary_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/test-collection-boundary_finalized
```

**Review notes:**

```text
docs/review/test-collection-boundary-review-*.md
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
git checkout -b feat/test-collection-boundary
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_test-collection-boundary.md
git commit -m "docs(plan): add test-collection-boundary implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Baseline: `./run.sh uv run pytest -q` (note current pass count).
2. `git mv scripts/test_ibis_batching.py scripts/test_nunique_nulls.py scripts/test_window_batching.py tests/`.
   Fix any imports broken by the move (these import `ibis`/`pandas`/`ibis_profiling`, not sibling
   scripts, so likely none). Ensure each is a valid pytest module.
3. `pyproject.toml` `[tool.pytest.ini_options]`: add `testpaths = ["tests"]`; set
   `pythonpath = ["src", "."]` (it is currently `["src"]`) so moved tests resolve imports.
4. Leave `scripts/test_financial_data.py` and `scripts/test_report_gen.py` in `scripts/` (now
   uncollected). Do not change their content.
5. Run `./run.sh uv run pytest -q`: the 3 moved tests run from `tests/`; no `scripts/` collection.

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

1. `./run.sh uv run pytest --collect-only -q | grep -c '^scripts/'` returns 0.
2. The 3 moved tests are collected from `tests/`; total real-test pass count >= baseline.
3. `scripts/orchestration/run-quality-gates` passes — regression gate 0 differences (no src change).

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished test-collection-boundary
```

This writes:

```text
/tmp/ibis-profiling/test-collection-boundary_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer test-collection-boundary`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/test-collection-boundary-review-*.md
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
   scripts/orchestration/clear-finished test-collection-boundary
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
   git add docs/review/test-collection-boundary-review-*.md
   git commit -m "docs(review): record test-collection-boundary review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished test-collection-boundary
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer test-collection-boundary` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed test-collection-boundary
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize test-collection-boundary
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/test-collection-boundary_finalized
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
scripts/orchestration/finalize test-collection-boundary
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/test-collection-boundary_finished
/tmp/ibis-profiling/test-collection-boundary_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
