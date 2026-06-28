# Plan: Add Duplicates Row-Count Guard

Add a row-count guard for duplicate row detection to prevent resource exhaustion and long execution times on large datasets.

## Problem Definition
Duplicate detection currently uses `table.distinct().count().execute()` unconditionally. For large datasets, this involves a full shuffle of the data across all columns, which can lead to memory exhaustion and excessive execution times. Benchmarking showed DuckDB handles 10M wide rows in ~7s, suggesting a high threshold is safe for modern backends but a guard is still needed for safety at extreme scales.

## Architecture Overview
The fix involves:
1.  Adding a `duplicates_threshold` parameter to the `Profiler` and `ProfileReport` APIs with a default of 50,000,000 rows.
2.  In `Profiler.run()`, check if `row_count > duplicates_threshold` before performing the duplicate check.
3.  Skip the check and emit a warning if the threshold is exceeded, unless the user explicitly requested duplicates (`compute_duplicates=True`).

## Key Files & Context
- `src/ibis_profiling/__init__.py`: Contains `Profiler.run`, `profile`, and `ProfileReport.__init__`.

## Proposed Solution
Update `src/ibis_profiling/__init__.py`:
-   Update `Profiler.__init__` to accept `duplicates_threshold: int = 50_000_000` and store `explicit_duplicates = compute_duplicates is True`.
-   Update `profile` function to accept `duplicates_threshold`.
-   Update `ProfileReport.__init__` to accept `duplicates_threshold`.
-   Update `Profiler.run` at the duplicate check block to check the threshold.

## Git Strategy
- **Branch:** `fix/duplicates-threshold`
- **Commits:**
  - Add duplicates_threshold to Profiler and ProfileReport APIs.
  - Implement row-count guard in duplicate check.
  - Add verification tests for duplicates threshold.

## Phased Approach

### Phase 1: Logic Implementation
- [ ] Modify `Profiler.__init__` in `src/ibis_profiling/__init__.py`:
    - Add `duplicates_threshold: int = 50_000_000` to the signature.
    - Set `self.duplicates_threshold = duplicates_threshold`.
    - Set `self.explicit_duplicates = compute_duplicates is True`.
- [ ] Modify `profile` function:
    - Add `duplicates_threshold: int = 50_000_000` to signature and pass it to `Profiler`.
- [ ] Modify `ProfileReport.__init__`:
    - Add `duplicates_threshold: int = 50_000_000` to signature and pass it to `profile`.
- [ ] Update `Profiler.run`:
    - Before calling `self.table.distinct().count().execute()`, check `row_count > self.duplicates_threshold`.
    - If `row_count > self.duplicates_threshold` and `not self.explicit_duplicates`, skip the check and add a warning to `report.analysis["warnings"]`.
    - Handle report metrics (set `n_distinct_rows` to `None` or "Skipped").

### Phase 2: Verification
- [ ] Create `tests/test_duplicates_threshold.py`.
- [ ] Test that for 10 rows (below threshold), duplicates are computed.
- [ ] Test that for 10 rows with threshold = 5, duplicates are skipped with a warning.
- [ ] Test that for 10 rows with threshold = 5 but `compute_duplicates=True`, duplicates are computed anyway.

## Testing Strategy
- **Threshold Check:** Verify `n_distinct_rows` is "Skipped" in the report when threshold is triggered.
- **Warning Verification:** Check that the report contains a warning about skipping duplicates.
- **Explicit Override:** Ensure `compute_duplicates=True` forces the check regardless of row count.
- **Minimal Mode:** Ensure `minimal=True` still skips duplicates.

## Technical Details
The warning message should clearly state the row count and the threshold used.
Example: `Skipped duplicate check for large dataset (60,000,000 rows). Threshold: 50,000,000 rows.`
