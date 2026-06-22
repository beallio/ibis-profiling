# Plan: Phase 3b-4b: extract ydata sections + App; index.jsx entry (all frontend modular) (ydata-sections-shell)

## Context

Finding 4 Phase 3b-4b — finish modularizing ydata-like (and thus the WHOLE frontend). Extract the 7
remaining section components and `App` from `frontend/ydata-like/index.jsx` into modules, leaving
`index.jsx` as just the entry (import App + ReactDOM mount). **Byte-identical render**; React/Lucide
stay GLOBAL.

Extract -> `frontend/ydata-like/components/`: `OverviewSection`, `VariableDetails`, `VariableCard`,
`MissingValuesSection`, `CorrelationsSection`, `SampleSection`, `InteractionsSection`.
Extract -> `frontend/ydata-like/App.jsx`: `App` (VERBATIM).

**Slug used throughout this plan:** `ydata-sections-shell`

---

## Orchestration Contract

**Slug:** `ydata-sections-shell`

**Plan file:**

```text
docs/plans/2026-06-22_ydata-sections-shell.md
```

**Implementation branch:**

```text
feat/ydata-sections-shell
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/ydata-sections-shell_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/ydata-sections-shell_finalized
```

**Review notes:**

```text
docs/review/ydata-sections-shell-review-*.md
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
git checkout -b feat/ydata-sections-shell
```

Commit this plan first:

```bash
git add docs/plans/2026-06-22_ydata-sections-shell.md
git commit -m "docs(plan): add ydata-sections-shell implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Oracles (byte-identical): e2e + DOM snapshot + visual. Do NOT
regenerate baselines.

1. Baseline: `./run.sh uv run pytest tests/test_e2e_frontend.py tests/test_e2e_frontend_snapshot.py tests/test_e2e_visual_regression.py -q`.
2. Move each of the 7 section components into `frontend/ydata-like/components/<Name>.jsx` VERBATIM +
   export. Add the imports each uses: `const { useState, useMemo, useEffect } = React;` (as used),
   `import { REPORT_DATA } from "../data.js";` / `import { <helpers> } from "../helpers.js";` as
   needed, and `import { <Leaf> } from "./<Leaf>.jsx";` for any leaf/sibling component it renders
   (e.g. VariableCard renders VariableDetails/HistogramChart; sections render StatRow/charts).
3. `frontend/ydata-like/App.jsx`: move `App` VERBATIM + export; import the hooks (global React), the
   section components it renders, and REPORT_DATA/helpers as used.
4. `index.jsx`: reduce to `import { App } from "./App.jsx";` + the existing
   `ReactDOM.createRoot(...).render(<App />)`. Remove all other defs/imports now unused there.
5. Rebuild `./run.sh uv run python scripts/build_templates.py`; ALL three oracles + full suite must
   pass byte-identically. Any diff = a wiring error; fix modules, never baselines.

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

1. `frontend/ydata-like/index.jsx` is a tiny entry; `App.jsx` + `components/` (13 total) +
   `data.js`/`helpers.js` make up the rest. Both themes are now fully modular.
2. React/ReactDOM/Lucide still globals (not imported).
3. `./run.sh uv run pytest` (full suite) green; all three oracles byte-identical; gates green.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished ydata-sections-shell
```

This writes:

```text
/tmp/ibis-profiling/ydata-sections-shell_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer ydata-sections-shell`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/ydata-sections-shell-review-*.md
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
   scripts/orchestration/clear-finished ydata-sections-shell
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
   git add docs/review/ydata-sections-shell-review-*.md
   git commit -m "docs(review): record ydata-sections-shell review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished ydata-sections-shell
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer ydata-sections-shell` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed ydata-sections-shell
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize ydata-sections-shell
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/ydata-sections-shell_finalized
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
scripts/orchestration/finalize ydata-sections-shell
```

Do not manually merge into `feat/frontend-modularization` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/ydata-sections-shell_finished
/tmp/ibis-profiling/ydata-sections-shell_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
