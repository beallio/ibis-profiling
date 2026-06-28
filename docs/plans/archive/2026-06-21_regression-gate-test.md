# Plan: Add pytest test that runs the JSON regression gate (on trunk) (regression-gate-test)

## Context

The standing JSON regression gate (`tools/regression/gate.py`) currently runs only via the
orchestration quality-gates hook — not in `pytest`/CI, so it does not guard ordinary PRs. Add a
pytest test that runs the gate against the committed baseline so any unintended change to the
profiler's `to_dict()` output (on the deterministic surface) fails the normal test suite.

Note: the gate profiles a 2M-row dataset single-threaded, so this test is SLOW (~20-40s incl.
regenerating the 106MB seeded parquet if absent). That is acceptable per the user's choice; mark it
so it is identifiable but keep it in the default suite.

Relevant files: `tools/regression/gate.py` (expose a callable `run_check() -> list[str]`); NEW
`tests/test_regression_gate.py`.

**Slug used throughout this plan:** `regression-gate-test`

---

## Orchestration Contract

**Slug:** `regression-gate-test`

**Plan file:**

```text
docs/plans/2026-06-21_regression-gate-test.md
```

**Implementation branch:**

```text
feat/regression-gate-test
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/regression-gate-test_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/regression-gate-test_finalized
```

**Review notes:**

```text
docs/review/regression-gate-test-review-*.md
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
git checkout -b feat/regression-gate-test
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_regression-gate-test.md
git commit -m "docs(plan): add regression-gate-test implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Refactor `tools/regression/gate.py` to expose `run_check() -> list[str]` returning the list of
   differences (empty == pass): move the body of `main()` that profiles, loads the baseline, and
   diffs into `run_check()`; have `main()` call it (preserve `--update-baseline` and exit codes /
   printing). No behavior change to the CLI.
2. Add `tests/test_regression_gate.py`:
   - `import` the gate module (add the `tools/regression` path or import via `tools.regression.gate`
     — match how the repo resolves `tools` given `pythonpath = ["src", "."]`).
   - `@pytest.mark.slow` (register the `slow` marker in `pyproject.toml` `[tool.pytest.ini_options]`
     `markers = [...]` to avoid the unknown-marker warning) on a `test_profiler_regression_gate()`
     that asserts `run_check() == []`, with a clear failure message pointing at
     `tools/regression/gate.py` and the baseline.
   - Skip cleanly (`pytest.skip`) if neither the dataset nor a working DuckDB/parquet path is
     available, so it never errors spuriously.
3. Confirm `./run.sh uv run pytest tests/test_regression_gate.py -q` runs the gate and passes.

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

1. `./run.sh uv run pytest tests/test_regression_gate.py -q` passes (runs the gate; 0 differences).
2. `gate.py` exposes `run_check()`; its CLI (`--update-baseline`, exit codes) still works:
   `./run.sh uv run python tools/regression/gate.py` prints PASS.
3. `scripts/orchestration/run-quality-gates` passes; the `slow` marker is registered (no marker
   warning). `ty check src/` + `ruff` clean.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished regression-gate-test
```

This writes:

```text
/tmp/ibis-profiling/regression-gate-test_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer regression-gate-test`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/regression-gate-test-review-*.md
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
   scripts/orchestration/clear-finished regression-gate-test
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
   git add docs/review/regression-gate-test-review-*.md
   git commit -m "docs(review): record regression-gate-test review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished regression-gate-test
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer regression-gate-test` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed regression-gate-test
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize regression-gate-test
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/regression-gate-test_finalized
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
scripts/orchestration/finalize regression-gate-test
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/regression-gate-test_finished
/tmp/ibis-profiling/regression-gate-test_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
