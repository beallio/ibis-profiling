# Plan: Phase 3b-0: pixel-level visual-regression oracle (screenshots) before component splitting (finding 4) (visual-regression-baseline)

## Context

Finding 4, **Phase 3b-0** — add a PIXEL-level visual-regression oracle BEFORE any component
splitting, so the upcoming modularization provably does not change the rendered charts/visuals. The
existing DOM snapshot oracle (`tests/test_e2e_frontend_snapshot.py`) captures SVG attributes +
classNames (structural), but not actual painted pixels. This adds screenshot regression as a second
oracle; every later 3b round must pass BOTH.

Deterministic by construction: pinned Playwright Chromium (same in dev + CI, both Linux), fixed
viewport, animations disabled, explicit wait-for-render. Report DATA is seeded
(`np.random.seed(42)` + `sample_seed=42`).

Relevant files: NEW `tests/test_e2e_visual_regression.py` (named `test_e2e_*` so the conftest skip
applies when Chromium is absent); NEW `tests/visual_baselines/` (committed PNG baselines);
`pyproject.toml` (add `pillow` to the dev group for PNG decode/diff — pinned, resolved under the
existing uv exclude-newer pin). No `src/` changes.

**Slug used throughout this plan:** `visual-regression-baseline`

---

## Orchestration Contract

**Slug:** `visual-regression-baseline`

**Plan file:**

```text
docs/plans/2026-06-21_visual-regression-baseline.md
```

**Implementation branch:**

```text
feat/visual-regression-baseline
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/visual-regression-baseline_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/visual-regression-baseline_finalized
```

**Review notes:**

```text
docs/review/visual-regression-baseline-review-*.md
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
git checkout -b feat/visual-regression-baseline
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_visual-regression-baseline.md
git commit -m "docs(plan): add visual-regression-baseline implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Add `pillow>=11.0.0` to `[dependency-groups] dev` in `pyproject.toml`; `./run.sh uv sync`.
2. Create `tests/test_e2e_visual_regression.py`:
   - Module fixture: the SAME seeded dataset shape as `tests/test_e2e_frontend.py`
     (`np.random.seed(42)`, 6 + correlated cols) -> `profile(table, title="Visual")` ->
     `report.to_file(path, theme=...)` for `theme in ("default", "ydata-like")`.
   - Use a Playwright context with `viewport={"width":1920,"height":1080}`, `device_scale_factor=1`,
     `reduced_motion="reduce"`. After `goto`, inject a style tag disabling motion:
     `* { animation: none !important; transition: none !important; caret-color: transparent !important; }`,
     wait for `#root` + a chart (`svg rect`/`.bg-blue-500`) so rendering is settled.
   - Capture PNGs: a full-page screenshot, plus per-section element screenshots by navigating to and
     screenshotting the chart container for: variables (histogram), correlations (heatmap),
     interactions (scatter), missing (nullity) — for BOTH themes (use the theme's nav as in
     `test_e2e_frontend.py`). Name each `<theme>__<view>.png`.
   - Compare with Pillow: decode baseline + actual to RGB (same size required); compute per-pixel
     max-channel difference; count pixels exceeding `PIXEL_THRESHOLD = 8`; assert
     `differing / total <= MAX_DIFF_RATIO` with `MAX_DIFF_RATIO = 0.002` (absorbs sub-pixel AA only).
     On failure, write `actual` + a red `diff` PNG to `/tmp/ibis-profiling/visual_artifacts/` and
     include the ratio + paths in the assertion message.
   - `IBIS_UPDATE_VISUAL_BASELINES=1` -> (re)write the baseline PNG instead of asserting.
   - `@pytest.mark.slow`.
3. Generate baselines: `IBIS_UPDATE_VISUAL_BASELINES=1 ./run.sh uv run pytest tests/test_e2e_visual_regression.py -q`.
   Then re-run WITHOUT the env var twice and confirm it PASSES both times (proves determinism; if a
   view is unstable, settle rendering / widen wait, do not loosen the ratio beyond ~0.002).
4. Drift sanity-check: temporarily change a chart fill color in `frontend/default/app.jsx`, rebuild
   (`./run.sh uv run python scripts/build_templates.py`), confirm the visual test FAILS for the
   affected view, then revert the change + rebuild so the tree is clean. (Document it was done.)
5. Commit `tests/visual_baselines/` + the test + the pyproject change.

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

1. `./run.sh uv run pytest tests/test_e2e_visual_regression.py -q` passes for both themes across all
   views, and is stable on repeated runs.
2. The drift sanity-check (task 4) caught a real color change and was reverted; tree clean.
3. `scripts/orchestration/run-quality-gates` passes (JSON gate 0; ruff/ty clean). Baselines are
   committed PNGs; the esbuild binary is NOT committed.
4. This establishes the pixel oracle; every subsequent 3b round must pass this test AND
   `tests/test_e2e_frontend_snapshot.py` (DOM) AND `tests/test_e2e_frontend.py`.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished visual-regression-baseline
```

This writes:

```text
/tmp/ibis-profiling/visual-regression-baseline_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer visual-regression-baseline`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/visual-regression-baseline-review-*.md
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
   scripts/orchestration/clear-finished visual-regression-baseline
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
   git add docs/review/visual-regression-baseline-review-*.md
   git commit -m "docs(review): record visual-regression-baseline review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished visual-regression-baseline
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer visual-regression-baseline` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed visual-regression-baseline
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize visual-regression-baseline
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/visual-regression-baseline_finalized
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
scripts/orchestration/finalize visual-regression-baseline
```

Do not manually merge into `main` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/visual-regression-baseline_finished
/tmp/ibis-profiling/visual-regression-baseline_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
