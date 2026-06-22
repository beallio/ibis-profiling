# Plan: Phase 3b-0 fix: mask volatile duration in full-page visual baseline; verify full suite (visual-baseline-mask-volatile)

## Context

Finding 4 Phase 3b-0 FIX. The visual-regression test's FULL-PAGE screenshots are non-deterministic:
they capture volatile rendered text — the "Analysis run <date>" (both themes) and "Job Duration
<ms/s>" (default, frontend/default/app.jsx ~776-782) — which changes every run. This makes
`tests/test_e2e_visual_regression.py` fail in the full suite (default full-page ~3163 px, ydata
~1599 px differ) even though nothing visual changed. The per-chart element crops are deterministic
and already pass; only the full-page header text is the problem. (The DOM oracle already normalizes
these via `_normalize`; the pixel oracle must MASK them.)

Fix: tag the volatile elements and mask them in the full-page screenshot (in both baseline
generation and comparison), then regenerate the full-page baselines. Verify against the FULL test
suite (the prior review only checked the test in isolation right after generating baselines — a
time-dependent false pass).

Relevant files: `frontend/default/app.jsx`, `frontend/ydata-like/app.jsx` (tag volatile elements),
`tests/test_e2e_visual_regression.py` (mask), `tests/test_e2e_frontend_snapshot.py` (`_normalize`
strip the new attribute so DOM baselines do not churn), regenerated `tests/visual_baselines/*full-page.png`,
rebuilt `src/ibis_profiling/templates/*.html`.

**Slug used throughout this plan:** `visual-baseline-mask-volatile`

---

## Orchestration Contract

**Slug:** `visual-baseline-mask-volatile`

**Plan file:**

```text
docs/plans/2026-06-21_visual-baseline-mask-volatile.md
```

**Implementation branch:**

```text
feat/visual-baseline-mask-volatile
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/visual-baseline-mask-volatile_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/visual-baseline-mask-volatile_finalized
```

**Review notes:**

```text
docs/review/visual-baseline-mask-volatile-review-*.md
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
3. Branch from `main`.
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

Start from `main`:

```bash
git checkout main
# ORCH_LOCAL_ONLY: local trial branch, skipping origin pull
git checkout -b feat/visual-baseline-mask-volatile
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_visual-baseline-mask-volatile.md
git commit -m "docs(plan): add visual-baseline-mask-volatile implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Identify EVERY volatile rendered region in the full page for BOTH themes by inspecting the
   rendered report (date/timestamp, job duration, and any elapsed/now value). At minimum: the
   "Analysis run ..." date (both themes) and the "Job Duration" value (default).
2. Add the attribute `data-visual-volatile=""` to each such element in `frontend/default/app.jsx`
   and `frontend/ydata-like/app.jsx`. Rebuild: `./run.sh uv run python scripts/build_templates.py`.
3. In `tests/test_e2e_visual_regression.py`, pass `mask=[page.locator("[data-visual-volatile]")]`
   to the FULL-PAGE `page.screenshot(full_page=True, ...)` call (Playwright paints the masked
   regions a flat color in both baseline and actual, making them deterministic). Leave the per-view
   element-crop screenshots unchanged.
4. In `tests/test_e2e_frontend_snapshot.py::_normalize`, add
   `re.sub(r'\s*data-visual-volatile=""', '', html)` so the new attribute is stripped and the
   existing committed DOM baselines still match (do NOT regenerate the DOM baselines).
5. Regenerate ONLY the full-page visual baselines:
   `IBIS_UPDATE_VISUAL_BASELINES=1 ./run.sh uv run pytest tests/test_e2e_visual_regression.py -q`.
6. VERIFY against the FULL suite (this is the key check): run `./run.sh uv run pytest` TWICE; both
   must be fully green (0 failures), including `test_e2e_visual_regression`,
   `test_e2e_frontend_snapshot`, and `test_e2e_frontend`.

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

1. `./run.sh uv run pytest` (the WHOLE suite) passes twice with 0 failures.
2. Sensitivity intact: recoloring the histogram bars (`bg-blue-500/60`) still fails the visual test;
   the masked date/duration no longer causes failures.
3. `scripts/orchestration/run-quality-gates` green. Only `*full-page.png` baselines changed; DOM
   snapshot baselines unchanged; esbuild binary not committed.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished visual-baseline-mask-volatile
```

This writes:

```text
/tmp/ibis-profiling/visual-baseline-mask-volatile_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer visual-baseline-mask-volatile`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/visual-baseline-mask-volatile-review-*.md
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
   scripts/orchestration/clear-finished visual-baseline-mask-volatile
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
   git add docs/review/visual-baseline-mask-volatile-review-*.md
   git commit -m "docs(review): record visual-baseline-mask-volatile review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished visual-baseline-mask-volatile
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer visual-baseline-mask-volatile` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed visual-baseline-mask-volatile
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize visual-baseline-mask-volatile
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/visual-baseline-mask-volatile_finalized
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
scripts/orchestration/finalize visual-baseline-mask-volatile
```

Do not manually merge into `main` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/visual-baseline-mask-volatile_finished
/tmp/ibis-profiling/visual-baseline-mask-volatile_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
