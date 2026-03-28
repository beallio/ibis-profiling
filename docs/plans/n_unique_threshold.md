# Plan: Add Size Guard for `n_unique` and other `value_counts` metrics

## Problem Definition
`n_unique` (singletons) uses `value_counts()` per column without any guard for row count or cardinality. On large (20M-50M+ rows) or high-cardinality datasets, this can be extremely slow and dominate profiling runtime.

## Architecture Overview
- `Profiler` and `profile` API now accept `n_unique_threshold` (default: 1,000,000).
- `QueryPlanner` uses this threshold to skip building `n_unique` and `top_values` expressions for columns that exceed both total row count AND distinct count thresholds.
- `QueryPlanner` optimizes `n_unique` by returning a literal value if a column is confirmed to be fully unique from Pass 1 metrics.
- `InternalProfileReport` now has a `finalize()` method called at the end of profiling to ensure derived metrics like `p_unique` are calculated after all data is collected.
- `Profiler._run_complex_pass` detects skipped metrics and adds a "Skipped" value and a descriptive warning to the report.

## Core Data Structures
- `n_unique_threshold`: Integer parameter in `Profiler`, `profile`, and `QueryPlanner`.
- `InternalProfileReport.variables[col]["n_unique"]`: Stores `"Skipped"` if threshold is exceeded.
- `InternalProfileReport.variables[col]["histogram"]`: Key is missing if `top_values` is skipped.
- `InternalProfileReport.variables[col]["warnings"]`: Stores a descriptive warning if skipped.

## Proposed Changes

### Phase 1: Logic
- [x] Add `n_unique_threshold` to `Profiler` and `profile`.
- [x] Add `n_unique_threshold` to `QueryPlanner`.
- [x] Implement skip logic in `QueryPlanner.build_complex_metrics` for `n_unique` and `top_values`.
- [x] Implement optimization for unique columns in `QueryPlanner.build_complex_metrics`.
- [x] Refactor `InternalProfileReport` to support late calculation of derived metrics via `finalize()`.
- [x] Implement warning logic in `Profiler._run_complex_pass`.

### Phase 2: CLI
- [x] Add `--n-unique-threshold` option to `ibis_profiling/cli.py`.
- [x] Pass the threshold from CLI to `ProfileReport`.

### Phase 3: Verification
- [x] Create `tests/test_n_unique_threshold.py`.
- [x] Create `tests/test_p_unique_fix.py`.
- [ ] Run full test suite to ensure no regressions.
- [x] Perform final performance benchmark to verify speedup on large datasets.

## Testing Strategy
- **Unit Tests:** `tests/test_n_unique_threshold.py` verifies the skip behavior and warning message using small datasets with artificially low thresholds. `tests/test_p_unique_fix.py` verifies derived metrics are updated.
- **Regression Tests:** Run all existing tests.
- **Benchmark:** Compare profiling time for a 50M row dataset with `n_unique_threshold` set to a low value vs `0` (disabled).

## Git Strategy
- Branch: `fix/n-unique-threshold`
- Commits: Individual commits for Logic, CLI, and Verification.
