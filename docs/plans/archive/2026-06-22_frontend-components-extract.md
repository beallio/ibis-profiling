# Plan: Phase 3b-2: extract leaf/chart components into components/ modules (default theme) (frontend-components-extract)

## Context

Finding 4 Phase 3b-2 (DEFAULT theme). Continue modularizing `frontend/default/index.jsx` by
extracting its 10 presentational/chart components and their shared helpers into ES modules bundled
by esbuild `--bundle`. **Behavior-preserving — byte-identical render**, verified by all three
oracles. Same conventions as 3b-1: React/ReactDOM/LucideReact stay GLOBAL (never imported);
ThemeContext/constants/helpers are imported.

Components to extract -> `frontend/default/components/<Name>.jsx`:
`ScatterPlot`, `StatCard`, `NumericHistogram`, `CategoricalChart`, `AlertBadge`,
`ExtremeValuesList`, `MetricRow`, `MetricsSection`, `NullityMatrix`,
`CorrelationMatrixComponent`.
Shared helpers used by them -> `frontend/default/helpers.js`: `parseMatrixData`,
`filterMissingBins`, `hasValidMetrics` (and any other small pure helper a component needs).

Relevant files: NEW `frontend/default/helpers.js`, `frontend/default/components/*.jsx`;
`frontend/default/index.jsx` (remove the moved code, add imports). ydata-like untouched.

**Slug used throughout this plan:** `frontend-components-extract`

---

## Orchestration Contract

**Slug:** `frontend-components-extract`

**Plan file:**

```text
docs/plans/2026-06-22_frontend-components-extract.md
```

**Implementation branch:**

```text
feat/frontend-components-extract
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/frontend-components-extract_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/frontend-components-extract_finalized
```

**Review notes:**

```text
docs/review/frontend-components-extract-review-*.md
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
3. Branch from `feat/frontend-modularization`.
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

Start from `feat/frontend-modularization`:

```bash
git checkout feat/frontend-modularization
# ORCH_LOCAL_ONLY: local trial branch, skipping origin pull
git checkout -b feat/frontend-components-extract
```

Commit this plan first:

```bash
git add docs/plans/2026-06-22_frontend-components-extract.md
git commit -m "docs(plan): add frontend-components-extract implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Oracles (all must stay green, byte-identical): e2e + DOM
snapshot + visual. Do NOT regenerate baselines.

1. Baseline: `./run.sh uv run pytest tests/test_e2e_frontend.py tests/test_e2e_frontend_snapshot.py tests/test_e2e_visual_regression.py -q`.
2. Create `frontend/default/helpers.js` and move `parseMatrixData`, `filterMissingBins`,
   `hasValidMetrics` there VERBATIM with `export`.
3. Create one module per component under `frontend/default/components/` (move VERBATIM, add
   `export`). In each module add only the imports it needs:
   - `const { useState, useMemo, useEffect, useContext } = React;` for whichever hooks it uses
     (React stays the global; do not `import` it),
   - `import { ThemeContext } from "../theme.js";` if it uses the theme,
   - `import { ALERT_CONFIG, THEMES, TYPE_LABELS } from "../constants.js";` as needed (e.g.
     AlertBadge uses ALERT_CONFIG),
   - `import { parseMatrixData, filterMissingBins, hasValidMetrics } from "../helpers.js";` as needed,
   - `import { <Sibling> } from "./<Sibling>.jsx";` if one component renders another.
   Lucide icons referenced via the global `LucideReact` stay as-is (no import).
4. In `index.jsx`, delete the moved component/helper definitions and add
   `import { <Name> } from "./components/<Name>.jsx";` for each (and the helpers if index.jsx still
   uses any). Keep `AppContent`/`App` and the mount in index.jsx.
5. Rebuild: `./run.sh uv run python scripts/build_templates.py`.
6. ALL three oracles + the full suite must pass. Any DOM/pixel diff = a wiring error (missing
   export/import, a hook not in scope, a helper not imported) — fix the modules, never the baseline.

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

1. `frontend/default/components/` has the 10 component modules; `helpers.js` has the shared helpers;
   `index.jsx` imports them and no longer defines them.
2. React/ReactDOM/Lucide are still globals (not imported anywhere).
3. `./run.sh uv run pytest` (full suite) green; all three frontend oracles byte-identical;
   `run-quality-gates` green. esbuild binary not committed.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished frontend-components-extract
```

This writes:

```text
/tmp/ibis-profiling/frontend-components-extract_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer frontend-components-extract`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/frontend-components-extract-review-*.md
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
   scripts/orchestration/clear-finished frontend-components-extract
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
   git add docs/review/frontend-components-extract-review-*.md
   git commit -m "docs(review): record frontend-components-extract review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished frontend-components-extract
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer frontend-components-extract` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed frontend-components-extract
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize frontend-components-extract
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/frontend-components-extract_finalized
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
scripts/orchestration/finalize frontend-components-extract
```

Do not manually merge into `feat/frontend-modularization` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/frontend-components-extract_finished
/tmp/ibis-profiling/frontend-components-extract_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
