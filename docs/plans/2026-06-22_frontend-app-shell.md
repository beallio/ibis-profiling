# Plan: Phase 3b-3: extract AppContent/App shell into modules; index.jsx becomes the entry (default fully modular) (frontend-app-shell)

## Context

Finding 4 Phase 3b-3 (DEFAULT theme) — final default extraction. `frontend/default/index.jsx`
(895 lines) still contains the big `AppContent` shell (~840 lines, with nested helpers
`getInitialTab`, `generateAlertMessage`, `getAlertsForVariable`) and the `App` root (theme state +
`ThemeContext.Provider`). Move `AppContent` and `App` into their own modules so `index.jsx` becomes
just the entry (imports + `ReactDOM.createRoot(...).render(<App />)`). After this the default theme
is FULLY modular. **Behavior-preserving — byte-identical render**, verified by all three oracles.
Conventions unchanged: React/ReactDOM/Lucide stay GLOBAL (never imported).

Relevant files: NEW `frontend/default/AppContent.jsx`, `frontend/default/App.jsx`;
`frontend/default/index.jsx` (reduced to the entry). ydata-like untouched.

**Slug used throughout this plan:** `frontend-app-shell`

---

## Orchestration Contract

**Slug:** `frontend-app-shell`

**Plan file:**

```text
docs/plans/2026-06-22_frontend-app-shell.md
```

**Implementation branch:**

```text
feat/frontend-app-shell
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/frontend-app-shell_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/frontend-app-shell_finalized
```

**Review notes:**

```text
docs/review/frontend-app-shell-review-*.md
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
git checkout -b feat/frontend-app-shell
```

Commit this plan first:

```bash
git add docs/plans/2026-06-22_frontend-app-shell.md
git commit -m "docs(plan): add frontend-app-shell implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Oracles (all must stay byte-identical): e2e + DOM snapshot +
visual. Do NOT regenerate baselines.

1. Baseline: `./run.sh uv run pytest tests/test_e2e_frontend.py tests/test_e2e_frontend_snapshot.py tests/test_e2e_visual_regression.py -q`.
2. `frontend/default/AppContent.jsx`: move `function AppContent() {...}` VERBATIM (its nested
   helpers move with it). Add the imports it uses: `const { useState, useMemo, useEffect, useContext
   } = React;` (whichever it uses), `import { ThemeContext } from "./theme.js";`,
   `import { THEMES, ALERT_CONFIG, TYPE_LABELS } from "./constants.js";` (as used),
   `import { REPORT_DATA } from "./data.js";`, `import { filterMissingBins, hasValidMetrics } from
   "./helpers.js";` (as used), and `import { <Name> } from "./components/<Name>.jsx";` for each of
   the 10 components it renders. `export function AppContent`.
3. `frontend/default/App.jsx`: move `function App() {...}` VERBATIM. Imports:
   `const { useState } = React;`, `import { ThemeContext } from "./theme.js";`,
   `import { AppContent } from "./AppContent.jsx";`, and constants if `getInitialTheme` uses them.
   `export function App`.
4. `frontend/default/index.jsx`: remove `AppContent`/`App` and their now-unused imports; keep just
   `import { App } from "./App.jsx";` and `const root = ReactDOM.createRoot(document.getElementById('root')); root.render(<App />);`.
5. Rebuild `./run.sh uv run python scripts/build_templates.py`; ALL three oracles + full suite must
   pass byte-identically. Any diff = a missing import/export or a hook out of scope — fix modules,
   never baselines.

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

1. `frontend/default/` is fully modular: `index.jsx` (entry only) + `App.jsx` + `AppContent.jsx` +
   `components/*.jsx` + `constants.js`/`data.js`/`theme.js`/`helpers.js`. `index.jsx` is small.
2. React/ReactDOM/Lucide still globals (not imported).
3. `./run.sh uv run pytest` (full suite) green; all three frontend oracles byte-identical;
   `run-quality-gates` green. esbuild binary not committed.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished frontend-app-shell
```

This writes:

```text
/tmp/ibis-profiling/frontend-app-shell_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer frontend-app-shell`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/frontend-app-shell-review-*.md
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
   scripts/orchestration/clear-finished frontend-app-shell
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
   git add docs/review/frontend-app-shell-review-*.md
   git commit -m "docs(review): record frontend-app-shell review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished frontend-app-shell
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer frontend-app-shell` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed frontend-app-shell
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize frontend-app-shell
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/frontend-app-shell_finalized
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
scripts/orchestration/finalize frontend-app-shell
```

Do not manually merge into `feat/frontend-modularization` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/frontend-app-shell_finished
/tmp/ibis-profiling/frontend-app-shell_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
