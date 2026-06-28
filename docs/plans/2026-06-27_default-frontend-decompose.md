# Plan: Decompose the default theme AppContent.jsx into shell + section components (finding 4) (default-frontend-decompose)

## Context

Thermo-nuclear review finding 4 (main, commit `d2b589d`). The `ydata-like` frontend is already
decomposed into per-section components, but the default theme keeps the entire application body in a
single 861-line `frontend/default/AppContent.jsx` (verified: largest tracked source file). That
file owns routing/active-tab state, derived report data, navigation construction, and every tab
section (overview, variable details, interactions, missing, correlations, duplicates, sample table,
mobile nav). It is preventive cleanup — no behavior bug — but it is close enough to the ~1k-line
smell that new feature work will push it over, and the rendered HTML must stay byte-stable.

The `ydata-like` theme is the reference target. It already has the structure to mirror
(`frontend/ydata-like/components/`):

```
OverviewSection.jsx  VariableDetails.jsx  VariableCard.jsx  InteractionsSection.jsx
MissingValuesSection.jsx  CorrelationsSection.jsx  SampleSection.jsx  ...
```

The default theme already extracts leaf components into `frontend/default/components/`
(`AlertBadge`, `CategoricalChart`, `CorrelationMatrixComponent`, `ExtremeValuesList`,
`MetricsSection`, `NullityMatrix`, `NumericHistogram`, `ScatterPlot`, `StatCard`). This round
extracts the remaining **section** and **shell** layers so `AppContent` becomes orchestration only.

This is a **behavior-preserving, render-identical refactor**. The non-negotiable guard is the
existing frontend snapshot / visual-regression baseline: the generated HTML must not change. This
is pure structure movement, no markup, class-name, or logic edits.

Relevant files:
- `frontend/default/AppContent.jsx` (split source).
- NEW `frontend/default/components/*.jsx` (extracted sections + shell).
- The default-theme build/bundle path (esbuild) and the snapshot/visual baseline under `tests/`
  / `tools/` — confirm the exact gate command before starting (see Implementation Tasks step 2).

**Slug used throughout this plan:** `default-frontend-decompose`

---

## Orchestration Contract

**Slug:** `default-frontend-decompose`

**Plan file:**

```text
docs/plans/2026-06-27_default-frontend-decompose.md
```

**Implementation branch:**

```text
feat/default-frontend-decompose
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/default-frontend-decompose_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/default-frontend-decompose_finalized
```

**Review notes:**

```text
docs/review/default-frontend-decompose-review-*.md
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
5. This is a render-identical refactor — the snapshot/visual baseline is the test; do not
   regenerate it.
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
git checkout -b feat/default-frontend-decompose
git add docs/plans/2026-06-27_default-frontend-decompose.md
git commit -m "docs(plan): add default-frontend-decompose implementation plan"
```

---

## Implementation Tasks

Work in small, individually-verified extractions. After EACH extraction, rebuild and run the
snapshot/visual gate — the HTML must be byte-identical at every step. Mirror the `ydata-like`
component boundaries and naming where they apply.

1. Baseline: build the default theme and capture the current generated HTML as the reference, then
   run the existing frontend snapshot / visual-regression gate to confirm it is green on a clean
   `main` checkout. Record the exact build + gate commands you used (e.g. `./run.sh ...`) at the top
   of the branch's first work commit message so reviewers can reproduce.
2. Identify the exact gate before touching code: locate the frontend snapshot / visual baseline
   test (grep `tests/` and `tools/` for "snapshot", "visual", "baseline", "esbuild") and confirm
   how it builds default-theme HTML. Do not proceed until you can run it red/green on demand.
3. Extract a `ReportShell` component (sidebar/header + mobile nav) into
   `frontend/default/components/ReportShell.jsx`. Pass active tab, search state, theme, and nav
   items as props. Rebuild + gate (HTML must be unchanged).
4. Extract tab sections one at a time, each its own commit + gate run, into
   `frontend/default/components/`:
   - `OverviewSection.jsx`
   - `VariablesSection.jsx` (variable list + details; reuse existing leaf components)
   - `InteractionsSection.jsx`
   - `MissingSection.jsx`
   - `CorrelationsSection.jsx`
   - `DuplicatesSection.jsx`
   - `SampleSection.jsx`
   Move markup verbatim; pass the data each section needs as props. No logic or class changes.
5. Move derived-report data and tab/nav construction out of `AppContent` into a small helper —
   either a `useReportViewModel` hook or a plain module (e.g.
   `frontend/default/reportViewModel.js`), consistent with how `ydata-like` organizes its
   `data.js`/`helpers.js`. Keep computations identical.
6. Reduce `AppContent` to orchestration only: load report data, hold active-tab/search state, and
   render `ReportShell` + the active section. Confirm imports resolve in the bundle.
7. Final rebuild + full gate run. Then sanity-check the line count dropped meaningfully:
   `wc -l frontend/default/AppContent.jsx` should be well under the prior 861.

---

## Quality Gates

Run before marking any round complete:

```bash
scripts/orchestration/run-quality-gates
scripts/orchestration/check-review-notes-not-deleted
git status --short
```

The round is not complete unless: all work is done; the frontend snapshot/visual gate is green with
no baseline regeneration; build/lint gates pass; review notes are not deleted; the working tree is
clean; all changes are committed.

---

## Verification

1. The default-theme generated HTML is byte-identical to the pre-refactor baseline (snapshot/visual
   gate green, baseline NOT regenerated).
2. `AppContent.jsx` is orchestration-only and substantially shorter than 861 lines.
3. New section + shell components exist under `frontend/default/components/` and mirror the
   `ydata-like` decomposition.
4. The default theme still builds/bundles cleanly (esbuild), and `./run.sh` end-to-end report
   generation works.
5. No markup, class-name, or behavior changes — diff is structure movement only.

---

## Mark Round Complete

```bash
scripts/orchestration/mark-finished default-frontend-decompose
```

Then exit cleanly. If the process exits, the orchestrator resumes you via
`scripts/orchestration/continue-implementer default-frontend-decompose`.

---

## Review Polling Loop

After marking complete, check existing review notes, then poll for new ones at
`docs/review/default-frontend-decompose-review-*.md`. When a note exists:

1. Read the full note.
2. If it ends with `STATUS: CHANGES_REQUESTED`, resume work.
3. Clear the marker: `scripts/orchestration/clear-finished default-frontend-decompose`.
4. Address every requested change.
5. Run quality gates (`run-quality-gates`, `check-review-notes-not-deleted`).
6. Commit code/docs fixes.
7. Commit the review-note file if not already committed:
   `git add docs/review/default-frontend-decompose-review-*.md && git commit -m "docs(review): record default-frontend-decompose review notes"`.
8. Recreate the marker: `scripts/orchestration/mark-finished default-frontend-decompose`.
9. Continue polling or exit cleanly.

---

## Approval Handling

If the latest review note ends with `STATUS: APPROVED`:

1. Confirm every prior item is addressed.
2. `scripts/orchestration/check-review-notes-committed default-frontend-decompose`.
3. `git status --short` (clean).
4. `scripts/orchestration/finalize default-frontend-decompose`.
5. Confirm `/tmp/ibis-profiling/default-frontend-decompose_finalized` exists.
6. Stop polling and exit cleanly.

---

## Review Rules

Do not write your own review. Do not create or delete files under `docs/review/`. Only the
orchestrator writes review notes; you read, resolve, and commit them as audit records.

---

## Finalization Rules

Only finalize after a `STATUS: APPROVED` note, via
`scripts/orchestration/finalize default-frontend-decompose`. Do not manually merge into `dev`
unless finalize fails and you are explicitly told to recover manually. Leave both markers in place
after finalization.
