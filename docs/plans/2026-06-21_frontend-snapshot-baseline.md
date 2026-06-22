# Plan: Phase 1: normalized DOM snapshot oracle for the rendered report (finding 4 prep) (frontend-snapshot-baseline)

## Context

Finding 4 (modular frontend build) prep — **Phase 1 of a tests-first approach**. Before any
frontend refactor, build a deterministic **DOM-snapshot oracle** of the currently-rendered report
so a later modular rewrite (Phase 3) can be proven to render identically. The rendered React UI has
only ~6 e2e selector tests today and no byte-identical oracle (unlike the JSON gate that protected
the Python findings).

**Dependency-free**: reuses the existing Playwright setup (the `page` fixture +
`tests/test_e2e_frontend.py` pattern). No new toolchain in this phase.

Determinism notes: report DATA is seeded (`np.random.seed(42)` + the profiler's `sample_seed=42`),
so rendering is deterministic — EXCEPT volatile bits that MUST be normalized before comparison:
- the CSP **nonce** (`secrets.token_hex(16)`, random every `to_html` call) — `nonce="..."` attrs,
- analysis **timestamps/duration** (`date_start`/`date_end`/`duration`),
- the **package version** string (hatch-vcs, changes per commit).

Relevant files: NEW `tests/test_e2e_frontend_snapshot.py` (named `test_e2e_*` so the existing
conftest skip applies when Chromium is absent); NEW `tests/frontend_baselines/` (committed
snapshots). No `src/` changes.

**Slug used throughout this plan:** `frontend-snapshot-baseline`

---

## Orchestration Contract

**Slug:** `frontend-snapshot-baseline`

**Plan file:**

```text
docs/plans/2026-06-21_frontend-snapshot-baseline.md
```

**Implementation branch:**

```text
feat/frontend-snapshot-baseline
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/frontend-snapshot-baseline_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/frontend-snapshot-baseline_finalized
```

**Review notes:**

```text
docs/review/frontend-snapshot-baseline-review-*.md
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
git checkout -b feat/frontend-snapshot-baseline
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_frontend-snapshot-baseline.md
git commit -m "docs(plan): add frontend-snapshot-baseline implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. Chromium is present locally, so the snapshot tests run.

1. Baseline: `./run.sh uv run pytest -q tests/test_e2e_frontend.py` (confirm Playwright works).
2. Create `tests/test_e2e_frontend_snapshot.py`:
   - Module fixture: a FIXED seeded dataset (reuse the shape in `test_e2e_frontend.py` —
     `np.random.seed(42)`, the same 6+correlated columns) -> `profile(table, title="Snapshot")` ->
     `report.to_file(path, theme=...)` for `theme in ("default", "ydata-like")`.
   - A `_normalize(html: str) -> str` helper that regex-replaces volatile content with stable
     placeholders: `nonce="[0-9a-f]+"` -> `nonce="X"`; ISO datetimes -> `DATE`; any "duration"/
     elapsed seconds -> `DUR`; the package version (import `ibis_profiling.__version__`) -> `VER`.
   - For each theme: `page.goto(file://...)`, `page.wait_for_selector("#root", state="visible")`,
     wait for first chart (`svg, .bg-blue-500`) so React has rendered, then capture the overview
     `page.inner_html("#root")`. Then click each main section (default: `button:has-text('Variables'|
     'Correlations'|'Missing'|'Interactions')`; ydata: the `a[href='#...']` links) and capture each
     section's `#root` inner_html. Normalize each capture.
   - Compare each normalized capture to a committed baseline file under
     `tests/frontend_baselines/<theme>__<section>.html`. If `IBIS_UPDATE_SNAPSHOTS=1`, (re)write the
     baseline instead of asserting; otherwise assert equality with a clear diff-pointing message.
   - `@pytest.mark.slow`.
3. Generate the baselines once: `IBIS_UPDATE_SNAPSHOTS=1 ./run.sh uv run pytest tests/test_e2e_frontend_snapshot.py -q`, then
   re-run WITHOUT the env var and confirm the snapshots now PASS (proves determinism after
   normalization — if a capture is unstable, widen `_normalize`, do not delete the assertion).
4. Sanity-check the oracle catches drift: temporarily tweak a rendered label in a `.src.html`,
   rebuild (`./run.sh uv run python scripts/build_templates.py`), confirm the snapshot test FAILS,
   then revert the tweak + rebuild so the tree is clean. (Document this was done; do not leave changes.)
5. Commit `tests/frontend_baselines/` + the test.

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

1. `IBIS_UPDATE_SNAPSHOTS` unset: `./run.sh uv run pytest tests/test_e2e_frontend_snapshot.py -q`
   passes (snapshots match) for both themes across the captured sections.
2. Re-running twice is stable (normalization removes nonce/date/version volatility).
3. The drift sanity-check (task 4) was performed and reverted; tree clean.
4. `scripts/orchestration/run-quality-gates` passes (no `src/` change; JSON gate 0 differences).
5. No new dependencies/toolchain added in this phase (esbuild comes in Phase 2, vendored).

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished frontend-snapshot-baseline
```

This writes:

```text
/tmp/ibis-profiling/frontend-snapshot-baseline_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer frontend-snapshot-baseline`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/frontend-snapshot-baseline-review-*.md
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
   scripts/orchestration/clear-finished frontend-snapshot-baseline
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
   git add docs/review/frontend-snapshot-baseline-review-*.md
   git commit -m "docs(review): record frontend-snapshot-baseline review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished frontend-snapshot-baseline
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer frontend-snapshot-baseline` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed frontend-snapshot-baseline
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize frontend-snapshot-baseline
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/frontend-snapshot-baseline_finalized
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
scripts/orchestration/finalize frontend-snapshot-baseline
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/frontend-snapshot-baseline_finished
/tmp/ibis-profiling/frontend-snapshot-baseline_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
