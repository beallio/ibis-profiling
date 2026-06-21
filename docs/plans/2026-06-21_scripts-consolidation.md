# Plan: Delete findings-broken scripts; add tools helpers (finding 6.2, on trunk) (scripts-consolidation)

## Context

Code-review finding 6 (increment 6.2, re-applied to origin/main): the `scripts/` directory holds
~59 ad-hoc one-off scripts. Two scoped actions (the user chose the conservative scope — keep the
remaining one-off scripts):
1. **Delete the scripts that earlier findings have BROKEN** (they reference APIs removed in findings
   2/3 and would now crash):
   `diagnose_20M_10cols.py`, `benchmark_parallel_safety.py`, `profile_5M_20cols.py`,
   `benchmark_parallel_comprehensive.py`, `benchmark_worker.py`,
   `generate_10m_20col_customer_data.py`, `profile_20M_13cols.py`, `generate_bench_data.py`,
   `profile_20M_20cols.py`, `generate_10M_empty_string_report.py`, `generate_test_data.py`
   (pass removed `parallel=`/`pool_size=`), and `bench_logical_inference_sampling.py`,
   `scale_test_inference_samples.py` (import logical-type classes removed in finding 3).
2. **Add three shared helper modules** so future scripting reuses them instead of copy-pasting:
   `tools/datasets.py` (parametrized synthetic-data generation), `tools/benchmark.py` (a small
   timing harness around `profile`), `tools/reports.py` (render an HTML/JSON report from a table).

Relevant files: the 13 scripts above (delete); NEW `tools/datasets.py`, `tools/benchmark.py`,
`tools/reports.py`. Do NOT delete or modify any other `scripts/*.py`. No `src/` changes.

**Slug used throughout this plan:** `scripts-consolidation`

---

## Orchestration Contract

**Slug:** `scripts-consolidation`

**Plan file:**

```text
docs/plans/2026-06-21_scripts-consolidation.md
```

**Implementation branch:**

```text
feat/scripts-consolidation
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/scripts-consolidation_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/scripts-consolidation_finalized
```

**Review notes:**

```text
docs/review/scripts-consolidation-review-*.md
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
git checkout -b feat/scripts-consolidation
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_scripts-consolidation.md
git commit -m "docs(plan): add scripts-consolidation implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Confirm each of the 13 listed scripts is broken/superseded (greps in the Context) and not
   imported by `src/` or `tests/`: `grep -rn "<modulename>" src tests` is empty for each. Then
   `git rm` all 13.
2. Create `tools/datasets.py`: a small, typed API for synthetic data, e.g.
   `generate_dataframe(*, rows, columns=..., seed=42) -> pl.DataFrame` and a
   `write_parquet(path, **kw)` helper, capturing the common shape of the deleted generators
   (numeric/text/categorical/datetime columns, seeded). Include a `if __name__ == "__main__":` CLI
   (argparse: --rows --cols --out).
3. Create `tools/benchmark.py`: `benchmark_profile(table, *, repeat=1, **profile_kwargs) -> dict`
   returning timing stats (min/mean/max seconds) around `ibis_profiling.profile`; small `__main__`
   CLI that benchmarks a parquet file.
4. Create `tools/reports.py`: `render_report(table, out_path, *, fmt="html"|"json", **profile_kwargs)`
   that profiles and writes the report (reuse `ProfileReport.to_html`/`to_dict`); small `__main__` CLI.
5. Add focused unit tests under `tests/` for the three helpers (each imports + a tiny smoke run):
   `tests/test_tools_helpers.py` — generate a small frame, benchmark a profile, render a JSON report
   to a tmp path; assert basic shape. Keep them fast (<= a few k rows).
6. `ruff`/`ty` clean; do not touch `src/` or the regression baseline.

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

1. The 13 listed scripts are gone; no other `scripts/*.py` changed: `git status` shows only the 13
   deletions + the 3 new `tools/*.py` + the new test.
2. `tools/datasets.py`, `tools/benchmark.py`, `tools/reports.py` import and their CLIs run.
3. `scripts/orchestration/run-quality-gates` passes — regression gate 0 differences (no src change);
   `tests/test_tools_helpers.py` green. `ty check src/` + `ruff` clean.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished scripts-consolidation
```

This writes:

```text
/tmp/ibis-profiling/scripts-consolidation_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer scripts-consolidation`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/scripts-consolidation-review-*.md
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
   scripts/orchestration/clear-finished scripts-consolidation
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
   git add docs/review/scripts-consolidation-review-*.md
   git commit -m "docs(review): record scripts-consolidation review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished scripts-consolidation
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer scripts-consolidation` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed scripts-consolidation
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize scripts-consolidation
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/scripts-consolidation_finalized
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
scripts/orchestration/finalize scripts-consolidation
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/scripts-consolidation_finished
/tmp/ibis-profiling/scripts-consolidation_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
