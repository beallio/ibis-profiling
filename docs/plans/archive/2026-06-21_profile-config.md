# Plan: Introduce typed ProfileConfig and unify divergent defaults (finding 1, on trunk) (profile-config)

## Context

Code-review finding 1 (re-applied to origin/main): the public config contract is duplicated and
drifted across `Profiler`, `profile()`, `ProfileReport`, the CLI, and the planner:
- `n_unique_threshold`: `Profiler`/`profile()` default `None`→`max(1_000_000, int(0.1*n_rows))`;
  `ProfileReport`/CLI/README default `50_000_000`.
- `global_batch_size`: `Profiler`/`profile()`/`ProfileReport` default `None`→dynamic
  (`MemoryManager.calculate_batch_size`); CLI/README default `500`; `QueryPlanner` has a dead
  `= 50` default (always overridden).

This round does two things: (A) introduce a single typed, immutable `ProfileConfig` that resolves
defaults + validation once and route `Profiler` through it; (B) **unify the divergent defaults**
to: `n_unique_threshold = 50_000_000` everywhere, `global_batch_size` = dynamic everywhere. (A) is
behavior-preserving; (B) intentionally changes `profile()` output (exact vs approximate `n_unique`
on large data) — the regression-gate baseline is regenerated as a conscious change.

Relevant files: NEW `src/ibis_profiling/config.py`, NEW `tests/test_config.py`;
`src/ibis_profiling/profiler.py` (build/route ProfileConfig; change `n_unique_threshold` default
`None`→`50_000_000` in `Profiler.__init__` and `profile()`, keeping `int | None` so explicit
`None` still computes); `src/ibis_profiling/cli.py` (`--global-batch-size` default `500`→`None`;
`--n-unique-threshold` stays `50_000_000`); `src/ibis_profiling/planner.py` (remove the dead
`global_batch_size: int = 50` default — make it required); `README.md` (`global_batch_size` row
`500`→"dynamic (memory-aware)"); `tools/regression/baseline_2M_20col.json` (regenerate);
tests that assume the bare computed default.

**Slug used throughout this plan:** `profile-config`

---

## Orchestration Contract

**Slug:** `profile-config`

**Plan file:**

```text
docs/plans/2026-06-21_profile-config.md
```

**Implementation branch:**

```text
feat/profile-config
```

**Round-complete marker:**

```text
/tmp/ibis-profiling/profile-config_finished
```

**Finalized marker:**

```text
/tmp/ibis-profiling/profile-config_finalized
```

**Review notes:**

```text
docs/review/profile-config-review-*.md
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
git checkout -b feat/profile-config
```

Commit this plan first:

```bash
git add docs/plans/2026-06-21_profile-config.md
git commit -m "docs(plan): add profile-config implementation plan"
```

---

## Implementation Tasks

All commands run through `./run.sh`. TDD where it applies.

1. Baseline: `./run.sh uv run pytest -q`.
2. Create `src/ibis_profiling/config.py`: `@dataclass(frozen=True) ProfileConfig` with a typed
   field for every resolved setting `Profiler` stores, plus `validation_warnings: tuple[str, ...]`.
   Add `@classmethod resolve(cls, *, n_rows, n_cols, <all Profiler.__init__ params except
   table/on_progress>) -> ProfileConfig` reproducing the current resolution EXACTLY:
   `n_unique_threshold None -> max(1_000_000, int(0.1*n_rows))`; `global_batch_size None ->
   MemoryManager.calculate_batch_size(n_rows, n_cols)`; `max(2, x)` clamps on the three
   `*_max_columns`; reset `correlations_sampling_threshold`/`correlations_sample_size` to
   `1_000_000` (appending a warning) when `<= 0`; the `compute_*`/`explicit_*` flag derivation.
3. `tests/test_config.py` (write before/with step 2): immutability; the None->computed
   resolutions; the clamps; the `<=0` validation warnings; the flag derivation.
4. Route `Profiler.__init__` through it: compute `n_rows`/`n_cols` (the early `count()`), build
   `self.config = ProfileConfig.resolve(...)`, set the existing instance attributes from
   `self.config`, and remove the now-duplicated inline resolution/clamp/validation. Keep the rest
   of `Profiler` untouched.
5. Unify defaults (behavior change for n_unique):
   - `Profiler.__init__` and `profile()`: `n_unique_threshold: int | None = None` -> `= 50_000_000`
     (keep the `None`->computed escape hatch in `resolve`).
   - CLI `--global-batch-size` default `500` -> `None`; `--n-unique-threshold` stays `50_000_000`.
   - `QueryPlanner.__init__`: remove the `= 50` default on `global_batch_size` (make it required).
   - `README.md`: `global_batch_size` row -> "dynamic (memory-aware)".
   - Update/adjust any test that assumed the bare `Profiler(...)`/`profile(...)` computed default.
6. **Regenerate the regression baseline (conscious change):**
   `./run.sh uv run python tools/regression/gate.py --update-baseline`, then inspect the diff and
   confirm it is limited to `n_unique`-related effects (n_unique/p_unique becoming exact, the
   "Unique values skipped..." warnings removed, value histograms appearing, and low-cardinality
   columns reclassified to `Categorical`) with NO numeric-stat (mean/std/variance/...) drift:
   `git --no-pager diff tools/regression/baseline_2M_20col.json | grep -E "^[-+]" | grep -viE "n_distinct|n_unique|p_unique|is_unique|distinct|warnings|histogram|logical_type|n_unique_threshold|Categorical|String|top_values|p_empty|n_empty" | head`
   should be empty. If a numeric stat changed, stop and investigate.

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

1. `scripts/orchestration/run-quality-gates` passes against the regenerated baseline (0 diffs).
2. `ProfileConfig` owns the resolution: `grep -nE "max\(2,|max\(1_000_000|calculate_batch_size|Resetting to default" src/ibis_profiling/profiler.py` returns nothing.
3. Unified defaults: `Profiler`/`profile()` `n_unique_threshold` default is `50_000_000`; CLI
   `--global-batch-size` default is `None`; `QueryPlanner` has no `= 50` default.
4. The regenerated baseline diff is n_unique-related only (no numeric drift), per step 6.
5. Deferred (out of scope here): routing `ProfileConfig` through `ProfileReport`/CLI/planner and a
   separate `ExcelReadConfig` (the 1c plumbing) — behavior-neutral, can follow later.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished profile-config
```

This writes:

```text
/tmp/ibis-profiling/profile-config_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer profile-config`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/profile-config-review-*.md
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
   scripts/orchestration/clear-finished profile-config
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
   git add docs/review/profile-config-review-*.md
   git commit -m "docs(review): record profile-config review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished profile-config
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer profile-config` after the next review note is created.

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
   scripts/orchestration/check-review-notes-committed profile-config
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize profile-config
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/ibis-profiling/profile-config_finalized
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
scripts/orchestration/finalize profile-config
```

Do not manually merge into `refactor/findings-on-trunk` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/ibis-profiling/profile-config_finished
/tmp/ibis-profiling/profile-config_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
