# Plan: Typed NumericStats/TextStats in VariableProfile (finding 5, increment 5c, on trunk) (typed-variable-stats)

## Context

Code-review finding 5 (increment 5c, re-applied to origin/main): in `report/models.py`,
`VariableProfile` keeps all numeric/text statistics in its untyped `extra` dict. Introduce typed
`NumericStats` and `TextStats` frozen dataclasses and have `VariableProfile` carry a typed
`stats: NumericStats | TextStats | None`, pulling the stat keys out of `extra`. **Behavior-preserving
— `to_dict()` output stays byte-identical** (regression gate is the oracle).

Relevant files: `src/ibis_profiling/report/models.py` (add the two dataclasses; thread through
`VariableProfile.from_internal`/`to_dict`). Safety net: `tests/test_report.py`,
`tests/test_report_components.py`, `tests/test_report_empty_strings.py`, `tests/test_summary.py`,
and the regression gate (every per-variable stat is on the compared surface).

**Slug used throughout this plan:** `typed-variable-stats`

---

## Orchestration Contract

**Slug:** `typed-variable-stats`

**Plan file:**

```text
docs/plans/2026-06-21_typed-variable-stats.md
```

**Implementation branch:**

```text
feat/typed-variable-stats
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/typed-variable-stats_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/typed-variable-stats_finalized
```

**Review notes:**

```text
docs/review/typed-variable-stats-review-*.md
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
git checkout -b feat/typed-variable-stats
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_typed-variable-stats.md
git commit -m "docs(plan): add typed-variable-stats implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. The oracle is byte-identity (gate 0 differences + report suite).

1. Baseline: `./run.sh uv run pytest -q tests/test_report.py tests/test_report_components.py tests/test_report_empty_strings.py tests/test_summary.py`.
2. Determine the numeric and text stat key sets empirically: profile a small numeric+text table and
   inspect a Numeric variable dict vs a String/Categorical one (the numeric-only keys are e.g.
   mean/std/variance/min/max/sum/median/mad/skewness/kurtosis/cv/iqr/range/the percentiles/
   n_zeros/p_zeros/n_negative/p_negative/n_infinite/p_infinite; text keys e.g. the length stats).
   Use the SAME key sets the profiler emits — do not guess; read them.
3. Add frozen `NumericStats` and `TextStats` to `models.py`, each following the existing pattern:
   typed fields for the known stat keys + `extra: dict` + `_present_fields: frozenset`, with
   `from_dict(d)` / `to_dict()` that round-trip exactly (emit only present fields, preserve order).
4. In `VariableProfile.from_internal`: if the variable `type` is Numeric, split the numeric stat
   keys into `NumericStats`; if it is the text-bearing type, split into `TextStats`; otherwise
   `stats=None`. Leave all non-stat keys in `extra`/scalars. In `VariableProfile.to_dict`, merge
   the stats fields back in their original position so the emitted dict is unchanged.
5. Run the gate continuously; any diff means a key was misrouted — fix the split, not the oracle.

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

1. `scripts/orchestration/run-quality-gates` passes — regression gate **0 differences** and the four
   report test files green.
2. `VariableProfile.stats` is typed `NumericStats | TextStats | None`; the stat keys live in the
   typed objects, not `extra`. `ty check src/` + `ruff` clean.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished typed-variable-stats
```

This writes:

```text
/tmp/ibis-profiling/typed-variable-stats_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer typed-variable-stats`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/typed-variable-stats-review-*.md
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
   scripts/orchestration/clear-finished typed-variable-stats
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
   git add docs/review/typed-variable-stats-review-*.md
   git commit -m "docs(review): record typed-variable-stats review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished typed-variable-stats
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer typed-variable-stats` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed typed-variable-stats
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize typed-variable-stats
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/typed-variable-stats_finalized
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
scripts/orchestration/finalize typed-variable-stats
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/typed-variable-stats_finished
/tmp/ibis-profiling/typed-variable-stats_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
