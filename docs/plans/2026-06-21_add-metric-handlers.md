# Plan: Dispatch add_metric through a handler table (finding 5, increment 5a, on trunk) (add-metric-handlers)

## Context

Code-review finding 5 (increment 5a, re-applied to origin/main): `ProfileReport.add_metric`
(`src/ibis_profiling/report/report.py`, ~303-376) is a long `if/elif` chain dispatching on
`metric_name` (`top_values`, `numeric_histogram`, `length_histogram`, `extreme_values_*`, generic).
Refactor into a small handler-dispatch (a lookup + focused handler methods), keeping the
head/tail-samples and `"Skipped"` short-circuits in `add_metric`. **Behavior-preserving** — the
report output is byte-identical.

Relevant files: `src/ibis_profiling/report/report.py` only. Safety net: `tests/test_report.py`,
`tests/test_report_components.py`, `tests/test_summary.py`, the regression gate (histograms/
top_values/extreme values are on the gate's compared surface).

**Slug used throughout this plan:** `add-metric-handlers`

---

## Orchestration Contract

**Slug:** `add-metric-handlers`

**Plan file:**

```text
docs/plans/2026-06-21_add-metric-handlers.md
```

**Implementation branch:**

```text
feat/add-metric-handlers
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/add-metric-handlers_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/add-metric-handlers_finalized
```

**Review notes:**

```text
docs/review/add-metric-handlers-review-*.md
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
git checkout -b feat/add-metric-handlers
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_add-metric-handlers.md
git commit -m "docs(plan): add add-metric-handlers implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Baseline: `./run.sh uv run pytest -q tests/test_report.py tests/test_report_components.py tests/test_summary.py`.
2. Extract each `metric_name` branch into a focused method on `ProfileReport`, each taking
   `(col_name, value)` and mutating `self.variables[col_name]` exactly as today:
   `_metric_top_values`, `_metric_numeric_histogram`, `_metric_length_histogram`,
   `_metric_extreme_values` (for the `extreme_values_*` prefix), `_metric_generic` (the `else`).
   Transcribe each body verbatim (the empty-string `(Empty)`/date isoformat handling in top_values;
   the constant-data branch + bin reconstruction in numeric_histogram; the `_to_json_serializable`
   paths). Keep the early `return` semantics (skipped, constant-histogram).
3. Build `_METRIC_HANDLERS = {"top_values": ..., "numeric_histogram": ..., "length_histogram": ...}`
   mapped to the methods. Rewrite `add_metric` to: handle `head`/`tail` -> samples; guard
   `col_name in self.variables`; handle `"Skipped"`; then if `metric_name` is in the table use that
   handler, elif it `startswith("extreme_values_")` use `_metric_extreme_values`, else
   `_metric_generic`.
4. Do not change `to_dict()` or any other method.

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

1. `scripts/orchestration/run-quality-gates` passes — regression gate 0 differences (histograms/
   top_values/extreme values byte-identical) and the report test suite green.
2. `add_metric` is now a short dispatcher; the per-metric logic lives in `_metric_*` handlers.
3. `ty check src/` + `ruff` clean.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished add-metric-handlers
```

This writes:

```text
/tmp/ibis-profiling/add-metric-handlers_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer add-metric-handlers`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/add-metric-handlers-review-*.md
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
   scripts/orchestration/clear-finished add-metric-handlers
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
   git add docs/review/add-metric-handlers-review-*.md
   git commit -m "docs(review): record add-metric-handlers review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished add-metric-handlers
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer add-metric-handlers` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed add-metric-handlers
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize add-metric-handlers
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/add-metric-handlers_finalized
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
scripts/orchestration/finalize add-metric-handlers
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/add-metric-handlers_finished
/tmp/ibis-profiling/add-metric-handlers_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
