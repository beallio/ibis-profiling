# Plan: Extract finalize derived-metrics/table-aggregation into pure functions (finding 5, increment 5d-1, on trunk) (finalize-pure-functions)

## Context

Code-review finding 5 (increment 5d-1, re-applied to origin/main): `ProfileReport.finalize()`
(`report.py`, ~180-end) interleaves two computations via in-place dict mutation and pervasive
`cast(int, self.table[...])`: (1) per-variable derived metrics (`p_missing`, `p_distinct`, `count`,
`is_unique`, `p_unique`, and Numeric `range`/`iqr`/`cv`/`p_zeros`/`p_infinite`/`p_negative`,
Categorical `p_empty` + pruning `NUMERIC_ONLY_METRICS`); (2) table-level aggregates
(`n_cells_missing`/`_empty`, `n_vars_constant`/`_with_missing`/`_all_missing`/`_with_empty`,
`p_cells_missing`/`_empty`). Extract both into **pure functions that return their results**, with
`finalize()` a thin orchestrator. **Behavior-preserving — output byte-identical** (gate is oracle).

Relevant files: `src/ibis_profiling/report/report.py` (`finalize` + two new helpers); NEW
`tests/test_finalize_helpers.py`. Safety net: `tests/test_report*.py`, `tests/test_summary.py`,
the regression gate.

**Slug used throughout this plan:** `finalize-pure-functions`

---

## Orchestration Contract

**Slug:** `finalize-pure-functions`

**Plan file:**

```text
docs/plans/2026-06-21_finalize-pure-functions.md
```

**Implementation branch:**

```text
feat/finalize-pure-functions
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/finalize-pure-functions_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/finalize-pure-functions_finalized
```

**Review notes:**

```text
docs/review/finalize-pure-functions-review-*.md
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
git checkout -b feat/finalize-pure-functions
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_finalize-pure-functions.md
git commit -m "docs(plan): add finalize-pure-functions implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Oracle: gate 0 differences + report suite.

1. Baseline: `./run.sh uv run pytest -q tests/test_report.py tests/test_report_empty_strings.py tests/test_summary.py tests/test_report_components.py`.
2. Add a pure `_derive_variable_metrics(stats: dict, n: int) -> dict` returning a NEW dict = copy of
   `stats` with the derived per-column fields applied and `NUMERIC_ONLY_METRICS` pruned for
   Categorical — reproducing the current loop body EXACTLY (the `"Skipped"`/non-numeric `n_distinct`
   passthrough for `p_distinct`; `is_unique=False` when `n_distinct` isn't numeric; the `mean != 0`
   guard for `cv`; per-type `p_*`; the categorical numeric-key pruning). Must not mutate its input.
3. Add a pure `_compute_table_aggregates(variables: dict, n: int) -> dict` returning all table-level
   derived fields (`n_cells_missing`, `n_cells_empty`, `n_vars_constant`, `n_vars_with_missing`,
   `n_vars_all_missing`, `n_vars_with_empty`, `p_cells_missing`, `p_cells_empty`) from the derived
   variables + `n` + `n_var` — reproducing the accumulation and `p_cells_* = count/(n*n_var)`
   formulas exactly (with divide-by-zero guards).
4. Rewrite `finalize()` as a thin orchestrator (keep `_finalized`/`table["n"]` guards + idempotency):
   `self.variables = {c: _derive_variable_metrics(s, n) for c, s in self.variables.items()}`;
   `self.table.update(_compute_table_aggregates(self.variables, n))`; keep the existing
   `self.alerts = AlertEngine.get_alerts(...)` and `self._finalized = True`. Remove the inline loop
   and the `cast(int, self.table[...])` accumulation it required.
5. `tests/test_finalize_helpers.py`: unit-test `_derive_variable_metrics` (Numeric range/iqr/cv/
   p_zeros/p_negative; Categorical p_empty + numeric-key pruning; `"Skipped"` n_distinct) and
   `_compute_table_aggregates` (constant/with-missing/with-empty vars); assert no input mutation.

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

1. `scripts/orchestration/run-quality-gates` passes — regression gate **0 differences** and the
   report suite green.
2. `finalize()` no longer contains the inline derivation loop / table accumulation or its `cast()`
   calls (only the benign `n = cast(int, self.table["n"])` read remains); the two helpers are pure.
3. `tests/test_finalize_helpers.py` covers them. `ty check src/` + `ruff` clean.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished finalize-pure-functions
```

This writes:

```text
/tmp/ibis-profiling/finalize-pure-functions_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer finalize-pure-functions`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/finalize-pure-functions-review-*.md
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
   scripts/orchestration/clear-finished finalize-pure-functions
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
   git add docs/review/finalize-pure-functions-review-*.md
   git commit -m "docs(review): record finalize-pure-functions review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished finalize-pure-functions
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer finalize-pure-functions` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed finalize-pure-functions
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize finalize-pure-functions
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/finalize-pure-functions_finalized
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
scripts/orchestration/finalize finalize-pure-functions
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/finalize-pure-functions_finished
/tmp/ibis-profiling/finalize-pure-functions_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
