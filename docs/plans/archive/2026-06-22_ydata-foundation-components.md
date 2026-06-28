# Plan: Phase 3b-4a: ydata-like -> index.jsx + extract data/helpers/leaf-components (bundle) (ydata-foundation-components)

## Context

Finding 4 Phase 3b-4a — begin modularizing the ydata-like theme (1060-line
`frontend/ydata-like/app.jsx`), mirroring the default theme. ydata-like has NO theme context and NO
THEMES/ALERT_CONFIG constants (simpler). This round: rename `app.jsx` -> `index.jsx` (so the build
bundles it via `--bundle`), and extract the data decode, the shared helpers, and the leaf/chart
components into modules. The section components and `App` stay in `index.jsx` for the next round
(3b-4b). **Behavior-preserving — byte-identical render**; React/ReactDOM/Lucide stay GLOBAL.

Extract -> `frontend/ydata-like/`:
- `data.js`: the `ENCODED_REPORT_DATA = "{{REPORT_DATA}}"` decode (export `REPORT_DATA`).
- `helpers.js`: `formatBytes`, `formatPct`, `formatNum`, `parseMatrixData`, `getAlertColor`.
- `components/`: `TypeIcon`, `HistogramChart`, `StatRow`, `NullityMatrix`,
  `CorrelationMatrixComponent`, `ScatterPlot`.
Keep in `index.jsx` (for 3b-4b): `OverviewSection`, `VariableDetails`, `VariableCard`,
`MissingValuesSection`, `CorrelationsSection`, `SampleSection`, `InteractionsSection`, `App`, mount.

**Slug used throughout this plan:** `ydata-foundation-components`

---

## Orchestration Contract

**Slug:** `ydata-foundation-components`

**Plan file:**

```text
docs/plans/2026-06-22_ydata-foundation-components.md
```

**Implementation branch:**

```text
feat/ydata-foundation-components
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/ydata-foundation-components_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/ydata-foundation-components_finalized
```

**Review notes:**

```text
docs/review/ydata-foundation-components-review-*.md
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
git checkout -b feat/ydata-foundation-components
```

Commit this plan first:

```bash
git add docs/plans/2026-06-22_ydata-foundation-components.md
git commit -m "docs(plan): add ydata-foundation-components implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Oracles (byte-identical): e2e + DOM snapshot + visual. Do NOT
regenerate baselines.

1. Baseline: `./run.sh uv run pytest tests/test_e2e_frontend.py tests/test_e2e_frontend_snapshot.py tests/test_e2e_visual_regression.py -q`.
2. `git mv frontend/ydata-like/app.jsx frontend/ydata-like/index.jsx`.
3. Create `frontend/ydata-like/data.js` (the decode; export `REPORT_DATA`) and `helpers.js`
   (the 5 helpers, exported). Move VERBATIM.
4. Create `frontend/ydata-like/components/<Name>.jsx` for the 6 leaf/chart components (VERBATIM +
   export). Add per-module imports: `const { useState, useMemo, useEffect } = React;` (whichever
   used; React stays global), `import { parseMatrixData, getAlertColor, ... } from "../helpers.js";`
   as needed, and sibling component imports if one renders another. Lucide via global `LucideReact`.
5. In `index.jsx`: remove the moved definitions; add `import { REPORT_DATA } from "./data.js";`,
   `import { <helpers> } from "./helpers.js";` (those still used by the remaining sections), and
   `import { <Name> } from "./components/<Name>.jsx";` for the 6 extracted components. Keep the
   section components + `App` + mount.
6. Rebuild `./run.sh uv run python scripts/build_templates.py` (it now bundles ydata-like/index.jsx).
   ALL three oracles + full suite must pass byte-identically. Any diff = wiring error; fix modules.

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

1. `frontend/ydata-like/` has `index.jsx` (no app.jsx), `data.js`, `helpers.js`, and
   `components/` with the 6 leaf/chart modules; sections + App still in index.jsx.
2. Build bundles ydata-like via `--bundle`; React/Lucide still globals.
3. `./run.sh uv run pytest` (full suite) green; all three oracles byte-identical; gates green.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished ydata-foundation-components
```

This writes:

```text
/tmp/ibis-profiling/ydata-foundation-components_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer ydata-foundation-components`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/ydata-foundation-components-review-*.md
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
   scripts/orchestration/clear-finished ydata-foundation-components
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
   git add docs/review/ydata-foundation-components-review-*.md
   git commit -m "docs(review): record ydata-foundation-components review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished ydata-foundation-components
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer ydata-foundation-components` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed ydata-foundation-components
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize ydata-foundation-components
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/ydata-foundation-components_finalized
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
scripts/orchestration/finalize ydata-foundation-components
```

Do not manually merge into `feat/frontend-modularization` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/ydata-foundation-components_finished
/tmp/ibis-profiling/ydata-foundation-components_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
