# Plan: Remove the `__` string-key contract from logical-type inference (finding 2) (logical-types-delimiter-fix)

## Context

Thermo-nuclear review finding 2 (main, commit `d2b589d`). Logical-type batch inference encodes
control flow in `__`-delimited alias strings and reparses them, which is **incorrect for column
names containing `__`**.

In `LogicalTypeInferrer.infer_batch` (`src/ibis_profiling/logical_types.py:595-658`):

- Aliases are built as `f"{col_name}__{logical_type.name}_{key}"` (`:619`).
- Chunk membership is decided by `key.split("__")[0] in chunk_cols` (`:630`).
- Result decoding uses `key.startswith(f"{col_name}__")` (`:644`) and
  `prefix = f"{col_name}__{logical_type.name}_"` (`:647`).

Two concrete failures for a column literally named `foo__bar`:

1. **Dropped inference.** `"foo__bar__Categorical_is_cat".split("__")[0]` -> `"foo"`, which is not
   in `chunk_cols` (it contains `"foo__bar"`). The column's check expressions are excluded from the
   aggregate, so it silently falls back to the dtype-based type.
2. **Cross-contamination.** If columns `foo` and `foo__bar` coexist, the decode step for column
   `foo` (`key.startswith("foo__")`, `:644`/`:647`) matches BOTH `foo__...` and `foo__bar__...`
   result keys, so `foo` absorbs `foo__bar`'s check results and can be misclassified.

The fix is to stop round-tripping typed facts through a delimiter-encoded string and instead keep
structured records, assigning opaque execution aliases only at the aggregate boundary with a
reverse map for decoding. This removes the `__` contract entirely.

Relevant files:
- `src/ibis_profiling/logical_types.py` (`infer_batch`, lines ~595-658).
- `tests/` (new regression coverage for `__` in column names; see Implementation Tasks).
- `tools/regression/baseline_2M_20col.json` — expected unaffected (baseline columns have no `__`);
  confirm 0 diffs, do not regenerate.

**Slug used throughout this plan:** `logical-types-delimiter-fix`

---

## Orchestration Contract

**Slug:** `logical-types-delimiter-fix`

**Plan file:**

```text
docs/plans/2026-06-27_logical-types-delimiter-fix.md
```

**Implementation branch:**

```text
feat/logical-types-delimiter-fix
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/logical-types-delimiter-fix_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/logical-types-delimiter-fix_finalized
```

**Review notes:**

```text
docs/review/logical-types-delimiter-fix-review-*.md
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
5. Follow TDD — write the failing `__`-column regression test first.
6. Run quality gates before marking any round complete.
7. Do not write your own review.
8. Do not create files under `docs/review/`.
9. Do not delete files under `docs/review/`.
10. Review notes are durable audit records and must be committed.
11. Resolving a review note means: implement changes; run quality gates; commit code/docs; commit
    the review note if not already committed; recreate the round-complete marker.
12. After finalization, stop polling and exit cleanly.

---

## Setup

```bash
git checkout dev
git pull --ff-only
git checkout -b feat/logical-types-delimiter-fix
git add docs/plans/2026-06-27_logical-types-delimiter-fix.md
git commit -m "docs(plan): add logical-types-delimiter-fix implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. TDD: the regression test must fail before the fix and pass
after.

1. Baseline: `./run.sh uv run pytest -q`.
2. Write a failing regression test (e.g. in the existing logical-types test module, or
   `tests/test_logical_types_delimiter.py`):
   - Build a small in-memory ibis table (e.g. via `ibis.memtable`) with a column whose name
     contains `__` and clearly belongs to a non-fallback logical type — e.g. a boolean-like column
     named `is__active` with values that should infer to `Boolean`, or a low-cardinality string
     column named `cat__col` that should infer to `Categorical`.
   - Assert `infer_batch` returns the expected logical type for that column (i.e. inference is NOT
     dropped to the dtype fallback).
   - Add a second case for cross-contamination: include both `foo` and `foo__bar` (or `x` and
     `x__y`) with deliberately different value profiles so they must infer to different logical
     types, and assert each column gets its own correct type (no bleed-through).
3. Refactor `infer_batch` to drop the `__` string contract. Suggested structure (implementer may
   choose an equivalent that removes the reparsing):
   - Build a list of chunk-local records, one per `(column, logical_type, check_name, expr)`,
     instead of the global `all_exprs` string-keyed map.
   - Assign opaque execution aliases at the aggregate boundary only — e.g. positional `c0`, `c1`,
     ... or `f"a{counter}"` — and keep a reverse map `alias -> (column, logical_type, check_name)`.
     The alias must not depend on column-name content.
   - Chunk by iterating the records grouped by column index (the existing `chunk_size = 5` over
     `cols` is fine); select the records whose column is in the current `chunk_cols` by object/value
     identity, not by string parsing.
   - After `aggregate(...).to_pyarrow().to_pydict()`, decode each result through the reverse map
     into `results[column][logical_type][check_name] = value`, then run the existing
     `logical_type.evaluate(type_results)` selection per column.
   - Preserve all existing behavior: `minimal` short-circuit (`:599`), the
     `inference_sample_size` head() sampling (`:603`), the Categorical/`n_unique_threshold` skip
     (`:612-617`), per-batch `try/except` with the same warning log (`:638-639`), and the
     fallback-type default (`get_fallback_type`) for columns with no usable results.
4. Remove the now-dead string helpers (`key.split("__")`, `startswith(f"{col_name}__")`,
   prefix-stripping) — verify none remain:
   `grep -n 'split("__")\|__")\|startswith(f"{col_name}' src/ibis_profiling/logical_types.py`.
5. Run the full suite: `./run.sh uv run pytest -q`.
6. Confirm the regression baseline is unchanged (its columns contain no `__`):
   `./run.sh uv run python tools/regression/gate.py` (or the project's gate entrypoint) must report
   0 diffs. Do NOT regenerate the baseline — a diff here means the refactor changed behavior for
   ordinary columns and must be investigated.

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

1. The `__`-column regression test fails on `main` and passes on the branch.
2. Cross-contamination test passes: `foo` and `foo__bar` each infer their own correct type.
3. No `__`-delimiter parsing remains in `logical_types.py` (grep from task 4 is empty).
4. Full suite passes: `./run.sh uv run pytest -q`.
5. Regression baseline shows 0 diffs (not regenerated).
6. Behavior for ordinary (no-`__`) columns is identical to `main`.

---

## Mark Round Complete

```bash
scripts/orchestration/mark-finished logical-types-delimiter-fix
```

Then exit cleanly. If the process exits, the orchestrator resumes you via
`scripts/orchestration/continue-implementer logical-types-delimiter-fix`.

---

## Review Polling Loop

After marking complete, check existing review notes, then poll for new ones at
`docs/review/logical-types-delimiter-fix-review-*.md`. When a note exists:

1. Read the full note.
2. If it ends with `STATUS: CHANGES_REQUESTED`, resume work.
3. Clear the marker: `scripts/orchestration/clear-finished logical-types-delimiter-fix`.
4. Address every requested change.
5. Run quality gates (`run-quality-gates`, `check-review-notes-not-deleted`).
6. Commit code/docs fixes.
7. Commit the review-note file if not already committed:
   `git add docs/review/logical-types-delimiter-fix-review-*.md && git commit -m "docs(review): record logical-types-delimiter-fix review notes"`.
8. Recreate the marker: `scripts/orchestration/mark-finished logical-types-delimiter-fix`.
9. Continue polling or exit cleanly.

---

## Approval Handling

If the latest review note ends with `STATUS: APPROVED`:

1. Confirm every prior item is addressed.
2. `scripts/orchestration/check-review-notes-committed logical-types-delimiter-fix`.
3. `git status --short` (clean).
4. `scripts/orchestration/finalize logical-types-delimiter-fix`.
5. Confirm `/tmp/ibis-profiling/logical-types-delimiter-fix_finalized` exists.
6. Stop polling and exit cleanly.

---

## Review Rules

Do not write your own review. Do not create or delete files under `docs/review/`. Only the
orchestrator writes review notes; you read, resolve, and commit them as audit records.

---

## Finalization Rules

Only finalize after a `STATUS: APPROVED` note, via
`scripts/orchestration/finalize logical-types-delimiter-fix`. Do not manually merge into `dev`
unless finalize fails and you are explicitly told to recover manually. Leave both markers in place
after finalization.
