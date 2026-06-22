# Plan: Extract Playwright bootstrap from run.sh (finding 7, on trunk) (runsh-bootstrap)

## Context

Code-review finding 7 (re-applied to origin/main): `run.sh` installs Playwright Chromium whenever
the browser directory is absent, so even read-only commands trigger a browser download. Make
`run.sh` env+exec only; move install to an explicit `scripts/bootstrap.sh` that checks the actual
Chromium executable (not just the directory); make e2e tests skip gracefully when Chromium is
absent so `./run.sh uv run pytest` and the gates pass without a hidden bootstrap.

Relevant files: `run.sh` (remove the install block; keep all `export`s incl. `PLAYWRIGHT_BROWSERS_PATH`),
NEW `scripts/bootstrap.sh` (executable), NEW `tests/conftest.py` (skip e2e when Chromium absent),
`README.md` (document the one-time bootstrap step). E2e tests: `tests/test_e2e_frontend.py`,
`tests/test_e2e_empty_strings_display.py`. (This trunk has no `AGENTS.md`; document in README only.)

**Slug used throughout this plan:** `runsh-bootstrap`

---

## Orchestration Contract

**Slug:** `runsh-bootstrap`

**Plan file:**

```text
docs/plans/2026-06-21_runsh-bootstrap.md
```

**Implementation branch:**

```text
feat/runsh-bootstrap
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/runsh-bootstrap_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/runsh-bootstrap_finalized
```

**Review notes:**

```text
docs/review/runsh-bootstrap-review-*.md
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
git checkout -b feat/runsh-bootstrap
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_runsh-bootstrap.md
git commit -m "docs(plan): add runsh-bootstrap implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`.

1. Baseline: `./run.sh uv run pytest -q` (Chromium currently present, so e2e run today).
2. Create executable `scripts/bootstrap.sh` (`set -Eeuo pipefail`): export the same env as run.sh,
   run `uv sync`, and ensure Chromium by checking the executable (not the dir):
   `if ! ls "$BROWSERS"/chromium-*/chrome-linux*/chrome >/dev/null 2>&1; then uv run playwright install chromium; else echo "already present"; fi` (idempotent).
3. Edit `run.sh`: delete the "Ensure Playwright Chromium is installed" block; keep all `export`
   lines (incl. `PLAYWRIGHT_BROWSERS_PATH`), the "Using environment" echo, and `exec "$@"`.
4. Create `tests/conftest.py` that skips `test_e2e_*` when Chromium is absent:
   a `pytest_collection_modifyitems` hook that, if `PLAYWRIGHT_BROWSERS_PATH` has no
   `chromium-*/chrome-linux*/chrome`, marks items whose nodeid contains `test_e2e` as skipped.
5. `README.md`: add a setup note that first-time/after-reboot setup is `./scripts/bootstrap.sh`
   (installs deps + Playwright Chromium); `run.sh` no longer does this.

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

1. `grep -nE "playwright install|Installing|mkdir" run.sh` returns nothing (env+exec only).
2. `scripts/bootstrap.sh` exists, executable, idempotent (checks the chrome executable).
3. `scripts/orchestration/run-quality-gates` passes — Chromium is present so e2e RUN; regression
   gate 0 differences.
4. Skip path works: `PLAYWRIGHT_BROWSERS_PATH=/tmp/nonexistent ./run.sh uv run pytest tests/test_e2e_frontend.py -q`
   shows the e2e tests SKIPPED (do not leave the override in place).
5. README mentions `./scripts/bootstrap.sh`.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished runsh-bootstrap
```

This writes:

```text
/tmp/ibis-profiling/runsh-bootstrap_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer runsh-bootstrap`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/runsh-bootstrap-review-*.md
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
   scripts/orchestration/clear-finished runsh-bootstrap
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
   git add docs/review/runsh-bootstrap-review-*.md
   git commit -m "docs(review): record runsh-bootstrap review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished runsh-bootstrap
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer runsh-bootstrap` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed runsh-bootstrap
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize runsh-bootstrap
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/runsh-bootstrap_finalized
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
scripts/orchestration/finalize runsh-bootstrap
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/runsh-bootstrap_finished
/tmp/ibis-profiling/runsh-bootstrap_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
