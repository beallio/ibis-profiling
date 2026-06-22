# Plan: Phase 3b-1: extract constants/context/data into modules; esbuild --bundle (default theme) (frontend-module-foundation)

## Context

Finding 4 Phase 3b-1 — first real modularization step (DEFAULT theme only). Today
`frontend/default/app.jsx` is one ~1440-line file compiled by esbuild as a single transform (3a).
Begin splitting it into ES modules bundled by esbuild `--bundle`, starting with the lowest-risk,
non-component pieces: constants, the React context, and the report-data decode. Components stay in
the entry file for now. **Behavior-preserving — the rendered report must be byte-identical**,
verified by all three oracles.

Key decisions (keep consistent for all 3b rounds):
- React / ReactDOM / LucideReact remain GLOBAL (referenced free, never `import`ed) so esbuild does
  not try to resolve them from node_modules — zero new runtime deps. esbuild `--bundle` leaves
  undefined globals alone.
- Bundle per theme from an `index.jsx` entry; `build_templates.py` bundles `index.jsx` if present,
  else falls back to the 3a single-file transform of `app.jsx` (so ydata-like is untouched here).

Relevant files: NEW `frontend/default/{index.jsx,constants.js,data.js,theme.js}` (from app.jsx),
delete `frontend/default/app.jsx`; `scripts/build_templates.py` (add `--bundle` path); rebuilt
`src/ibis_profiling/templates/default.html`. ydata-like unchanged.

**Slug used throughout this plan:** `frontend-module-foundation`

---

## Orchestration Contract

**Slug:** `frontend-module-foundation`

**Plan file:**

```text
docs/plans/2026-06-22_frontend-module-foundation.md
```

**Implementation branch:**

```text
feat/frontend-module-foundation
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/frontend-module-foundation_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/frontend-module-foundation_finalized
```

**Review notes:**

```text
docs/review/frontend-module-foundation-review-*.md
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
git checkout -b feat/frontend-module-foundation
```

Commit this plan first:

```bash
git add docs/plans/2026-06-22_frontend-module-foundation.md
git commit -m "docs(plan): add frontend-module-foundation implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Oracles (must all pass): `tests/test_e2e_frontend_snapshot.py`
(DOM, exact), `tests/test_e2e_visual_regression.py` (pixel, local), `tests/test_e2e_frontend.py` (e2e).
Do NOT regenerate any baseline — byte-identical rendering is the requirement.

1. Baseline: `./run.sh uv run pytest tests/test_e2e_frontend.py tests/test_e2e_frontend_snapshot.py tests/test_e2e_visual_regression.py -q`.
2. Split `frontend/default/app.jsx` into modules (move code VERBATIM, only adding `export`/`import`):
   - `constants.js`: `export const THEMES`, `ALERT_CONFIG`, `TYPE_LABELS` (and any other pure-data consts).
   - `data.js`: the `ENCODED_REPORT_DATA = "{{REPORT_DATA}}"` decode; `export` the resulting
     `REPORT_DATA` (keep the `{{REPORT_DATA}}` string literal intact).
   - `theme.js`: `export const ThemeContext = React.createContext();` (React stays global).
   - `index.jsx`: the rest (all components + the `ReactDOM.createRoot(...).render(...)` mount), with
     `import { THEMES, ALERT_CONFIG, TYPE_LABELS } from "./constants.js";`,
     `import { REPORT_DATA } from "./data.js";`, `import { ThemeContext } from "./theme.js";`.
     Keep the existing `const { useState, ... } = React;` destructuring in index.jsx.
   - `git rm frontend/default/app.jsx`.
3. `scripts/build_templates.py`: for each theme, if `frontend/<theme>/index.jsx` exists, run esbuild
   with `--bundle` on it: `<esbuild> frontend/<theme>/index.jsx --bundle --format=iife
   --jsx=transform --jsx-factory=React.createElement --jsx-fragment=React.Fragment` (NO --minify, NO
   --target); else keep the existing single-file `--jsx=transform` of `app.jsx`. Inject the output
   at the template marker exactly as today. Resolve esbuild from the lock manifest.
4. Rebuild: `./run.sh uv run python scripts/build_templates.py`.
5. ALL oracles must pass: `./run.sh uv run pytest tests/test_e2e_frontend.py
   tests/test_e2e_frontend_snapshot.py tests/test_e2e_visual_regression.py -q`. If a snapshot/pixel
   differs, the bundle output changed the render — fix the module split (a missing export, a scope
   change), do NOT touch baselines.

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

1. `frontend/default/` is now `index.jsx` + `constants.js` + `data.js` + `theme.js` (no `app.jsx`);
   ydata-like still has `app.jsx`.
2. `scripts/build_templates.py` bundles default via `--bundle`, ydata via the transform fallback.
3. ALL THREE oracles pass (DOM byte-identical, pixel within budget, e2e), AND the FULL suite:
   `./run.sh uv run pytest` is green. `run-quality-gates` green. esbuild binary not committed.
4. React/ReactDOM/Lucide are not imported anywhere (still globals).

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished frontend-module-foundation
```

This writes:

```text
/tmp/ibis-profiling/frontend-module-foundation_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer frontend-module-foundation`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/frontend-module-foundation-review-*.md
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
   scripts/orchestration/clear-finished frontend-module-foundation
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
   git add docs/review/frontend-module-foundation-review-*.md
   git commit -m "docs(review): record frontend-module-foundation review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished frontend-module-foundation
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer frontend-module-foundation` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed frontend-module-foundation
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize frontend-module-foundation
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/frontend-module-foundation_finalized
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
scripts/orchestration/finalize frontend-module-foundation
```

Do not manually merge into `feat/frontend-modularization` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/frontend-module-foundation_finished
/tmp/ibis-profiling/frontend-module-foundation_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
