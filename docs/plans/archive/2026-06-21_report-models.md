# Plan: Serialize through a typed ReportModel (finding 5, increment 5b, on trunk) (report-models)

## Context

Code-review finding 5 (increment 5b, re-applied to origin/main): `ProfileReport` serializes by
hand-assembling nested dicts in `to_dict()`. Introduce a typed model boundary: frozen dataclasses
in a new `src/ibis_profiling/report/models.py` that capture the report's state and re-emit the
EXACT same dict, then route `ProfileReport.to_dict()` through it. **Behavior-preserving — the
serialized output must be byte-identical** (the regression gate compares `to_dict()` output).

Relevant files: NEW `src/ibis_profiling/report/models.py`; `src/ibis_profiling/report/report.py`
(`to_dict` routes through the model; keep `_clean_dict`/`_format_matrices`/`_to_json_serializable`
helpers and `finalize`). Safety net: `tests/test_report.py`, `tests/test_report_components.py`,
`tests/test_report_empty_strings.py`, `tests/test_summary.py`, and the regression gate.

**Slug used throughout this plan:** `report-models`

---

## Orchestration Contract

**Slug:** `report-models`

**Plan file:**

```text
docs/plans/2026-06-21_report-models.md
```

**Implementation branch:**

```text
feat/report-models
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/report-models_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/report-models_finalized
```

**Review notes:**

```text
docs/review/report-models-review-*.md
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
git checkout -b feat/report-models
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_report-models.md
git commit -m "docs(plan): add report-models implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. **The oracle is byte-identity**: `run-quality-gates` (gate 0
differences) + the report test suite. Iterate until both are green; never change a test or the
baseline to accommodate a structural drift.

1. Baseline: `./run.sh uv run pytest -q tests/test_report.py tests/test_report_components.py tests/test_report_empty_strings.py tests/test_summary.py`.
2. Create `src/ibis_profiling/report/models.py` with frozen dataclasses:
   - `Alert` (the alert dict shape), `AnalysisMetadata` (the `analysis` section),
     `TableProfile` (the `table` section), `VariableProfile` (one `variables[col]` entry:
     typed common-core scalar fields + an `extra: dict` for any remaining keys + a
     `_present_fields: frozenset[str]` recording exactly which keys were present), and a top-level
     `ReportModel` holding analysis, table, variables, correlations, interactions, missing, alerts,
     samples, package.
   - `@classmethod from_internal(cls, report) -> ReportModel` reads `report.analysis`,
     `report.table`, `report.variables`, `report.correlations`, `report.interactions`,
     `report.missing`, `report.alerts`, `report.samples`, and the package version, recording
     present fields so absent keys are not invented.
   - `to_dict(self) -> dict` reconstructs the SAME structure `ProfileReport.to_dict` produced
     pre-cleaning, preserving key order and omit-absent behavior via `_present_fields`/`extra`.
3. Route `ProfileReport.to_dict`: call `self.finalize()`, then
   `d = ReportModel.from_internal(self).to_dict()`, then apply the existing
   `self._format_matrices` (correlations + missing) and `self._clean_dict(d)` exactly as today so
   the final output is unchanged. (If cleaner, fold the matrix formatting into the model, but only
   if the gate stays at 0 differences.)
4. Run the gate continuously. Any difference means a field was dropped/reordered/invented — fix the
   model, not the oracle.

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

1. `scripts/orchestration/run-quality-gates` passes — regression gate **0 differences** (full
   `to_dict()` output byte-identical) and the four report test files green.
2. `ProfileReport.to_dict` routes through `ReportModel.from_internal(self).to_dict()`.
3. `models.py` dataclasses are frozen; `_present_fields` preserves omit-absent fidelity.
   `ty check src/` + `ruff` clean.
4. Deferred to 5c: typing the per-variable `stats` as `NumericStats`/`TextStats` (here `extra`/
   scalars suffice for byte-identity).

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished report-models
```

This writes:

```text
/tmp/ibis-profiling/report-models_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer report-models`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/report-models-review-*.md
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
   scripts/orchestration/clear-finished report-models
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
   git add docs/review/report-models-review-*.md
   git commit -m "docs(review): record report-models review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished report-models
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer report-models` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed report-models
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize report-models
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/report-models_finalized
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
scripts/orchestration/finalize report-models
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/report-models_finished
/tmp/ibis-profiling/report-models_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
