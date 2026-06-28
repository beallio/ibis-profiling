# Plan: Phase 3a: build report JS via vendored esbuild instead of in-browser Babel (finding 4) (esbuild-build-swap)

## Context

Finding 4, **Phase 3a** — swap ONLY the build mechanism, no component splitting yet, so any
regression is attributable to esbuild (not refactoring). Today `scripts/build_templates.py`
transpiles the inline `<script type="text/babel">` JSX by launching Playwright + running
`@babel/standalone` in a headless browser. Replace that with a static transform by the **vendored
esbuild** (Phase 2). The app uses GLOBAL `React`/`ReactDOM`/`LucideReact` (no imports), so this is a
pure JSX transform — no bundling/module-resolution required.

**Behavior-preserving — the rendered report must be byte-identical**, verified by the Phase-1 DOM
snapshot oracle (`tests/test_e2e_frontend_snapshot.py`, which renders through the BUILT
`templates/*.html`).

Relevant files: `src/ibis_profiling/templates/default.src.html` + `ydata-like.src.html` (extract the
JSX); NEW `frontend/default/app.jsx` + `frontend/ydata-like/app.jsx`; `scripts/build_templates.py`
(rewrite to use esbuild); the built `templates/*.html` (regenerated). esbuild binary at the
`install_path` from `tools/frontend/esbuild.lock.json` (`./scripts/bootstrap.sh` provisions it).

**Slug used throughout this plan:** `esbuild-build-swap`

---

## Orchestration Contract

**Slug:** `esbuild-build-swap`

**Plan file:**

```text
docs/plans/2026-06-21_esbuild-build-swap.md
```

**Implementation branch:**

```text
feat/esbuild-build-swap
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/esbuild-build-swap_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/esbuild-build-swap_finalized
```

**Review notes:**

```text
docs/review/esbuild-build-swap-review-*.md
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
git checkout -b feat/esbuild-build-swap
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_esbuild-build-swap.md
git commit -m "docs(plan): add esbuild-build-swap implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Oracle: `tests/test_e2e_frontend_snapshot.py` must stay green
(do NOT regenerate the baselines — they are the proof esbuild output renders identically).

1. Ensure esbuild present: `./scripts/bootstrap.sh` (idempotent). Baseline the oracle:
   `./run.sh uv run pytest tests/test_e2e_frontend_snapshot.py -q` (passes today).
2. For each theme in (`default`, `ydata-like`): extract the FULL contents of the
   `<script type="text/babel"> ... </script>` block from `<theme>.src.html` VERBATIM into
   `frontend/<theme>/app.jsx` (keep any `{{REPORT_DATA}}`/`{{NONCE}}` string literals as-is).
   In the `.src.html`, replace the babel block's inner content with a build marker
   `<!-- {{APP_BUNDLE}} -->` (keep the surrounding `<script ...>` tag structure or replace the whole
   block — your choice, as long as the build can target it deterministically).
3. Rewrite `scripts/build_templates.py` to NOT use Playwright/Babel/pandas/numpy/ibis. For each
   `*.src.html`: run the vendored esbuild as a static transform of the theme's `app.jsx`:
   `<esbuild> frontend/<theme>/app.jsx --loader=jsx --jsx=transform --jsx-factory=React.createElement
   --jsx-fragment=React.Fragment` (NO `--minify`, NO `--target` down-leveling — match Babel
   preset-react which only transforms JSX). Capture stdout as the compiled JS (placeholders
   preserved as literals). Resolve the esbuild path from `tools/frontend/esbuild.lock.json`
   `install_path`; if absent, print "run ./scripts/bootstrap.sh" and exit non-zero.
4. Inject the compiled JS into the `.src.html` shell at the marker as
   `<script nonce="{{NONCE}}" type="text/javascript">...compiled...</script>`, remove the Babel CDN
   `<script src="https://unpkg.com/@babel/standalone/...">` and its comment, and write
   `templates/<theme>.html`. Keep everything else (head, styles, `{{REPORT_DATA}}` data script,
   `#root`) unchanged.
5. Rebuild: `./run.sh uv run python scripts/build_templates.py`. Then the oracle MUST pass:
   `./run.sh uv run pytest tests/test_e2e_frontend_snapshot.py tests/test_e2e_frontend.py -q`.
   If a snapshot differs, esbuild output is not equivalent — fix the esbuild invocation (jsx
   factory/fragment, target), do NOT edit the baselines.

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

1. `scripts/build_templates.py` uses the vendored esbuild only — no `playwright`/`Babel`/`pandas`/
   `numpy`/`ibis` imports remain in it.
2. `frontend/default/app.jsx` + `frontend/ydata-like/app.jsx` exist (extracted JSX); the
   `.src.html` files no longer contain the Babel CDN script.
3. `./run.sh uv run pytest tests/test_e2e_frontend_snapshot.py tests/test_e2e_frontend.py -q`
   passes (rendered DOM byte-identical to the Phase-1 baselines → esbuild ≡ Babel output).
4. `scripts/orchestration/run-quality-gates` passes (JSON gate 0; ruff/ty clean). The vendored
   esbuild binary is NOT committed (lives in /tmp).
5. Deferred to Phase 3b+: splitting `app.jsx` into component/hook/style modules (esbuild `--bundle`).

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished esbuild-build-swap
```

This writes:

```text
/tmp/ibis-profiling/esbuild-build-swap_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer esbuild-build-swap`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/esbuild-build-swap-review-*.md
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
   scripts/orchestration/clear-finished esbuild-build-swap
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
   git add docs/review/esbuild-build-swap-review-*.md
   git commit -m "docs(review): record esbuild-build-swap review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished esbuild-build-swap
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer esbuild-build-swap` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed esbuild-build-swap
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize esbuild-build-swap
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/esbuild-build-swap_finalized
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
scripts/orchestration/finalize esbuild-build-swap
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/esbuild-build-swap_finished
/tmp/ibis-profiling/esbuild-build-swap_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
