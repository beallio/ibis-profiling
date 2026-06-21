# Review — profile-config (round 01, trunk re-apply)

Branch: `feat/profile-config` (base `refactor/findings-on-trunk`)
Commit reviewed: `a0dbeb7`

## Verdict

Approved. Re-applies finding 1 (core) to origin/main:
- New frozen `ProfileConfig` (`config.py`) + `resolve()` owns all default resolution/clamps/
  validation; `Profiler` routed through it (inline logic removed).
- Defaults unified: `n_unique_threshold` -> `50_000_000` in `Profiler`/`profile()` (`int | None`
  kept for the computed escape hatch); CLI `--global-batch-size` -> `None` (dynamic); planner's
  dead `= 50` default removed; README updated. `tests/test_config.py` added.

## Gate status — regenerated baseline reviewed

Behavior intentionally changes (n_unique). The regenerated baseline diff is confined to the
expected effects (structural diff): `n_unique`/`p_unique` exact (8 cols), "skipped" warnings
removed (8), value histograms appear (2), 3 low-cardinality columns reclassified `Categorical`,
`analysis.n_unique_threshold` 1M->50M — and **zero numeric-stat drift** (mean/std/variance/... all
identical). `run-quality-gates` passes against the regenerated baseline (0 diffs).

## Deferred (1c)

Routing `ProfileConfig` through `ProfileReport`/CLI/planner + separate `ExcelReadConfig`
(behavior-neutral plumbing) — optional follow-up.

## Finalization

`scripts/orchestration/finalize profile-config` (local merge into `refactor/findings-on-trunk`).

STATUS: APPROVED
