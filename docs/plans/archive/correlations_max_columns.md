# Plan: Cap Correlation Matrix Size

Add a column cap for correlation matrices to prevent $O(n^2)$ resource exhaustion on wide datasets.

## Problem Definition
Calculating correlations for wide datasets (e.g., 500+ numeric columns) results in a massive number of pairwise operations ($n^2$), which can lead to slow execution times and memory exhaustion. Currently, `ibis-profiling` attempts to compute correlations for all numeric columns without any limits.

## Architecture Overview
The fix involves:
1.  Adding a `correlations_max_columns` parameter to the `Profiler` and `ProfileReport` APIs (default: 15).
2.  Implementing a deterministic column selection strategy in `CorrelationEngine.compute_all` to pick the "best" columns when truncation is necessary.
3.  Selection criteria: Sort columns by `n_missing` ascending (less missingness is better) and `variance` descending (more variation is more informative).
4.  Adding a warning to the report when truncation occurs.

## Key Files & Context
- `src/ibis_profiling/report/model/correlations.py`: Main logic for correlation computation.
- `src/ibis_profiling/__init__.py`: `Profiler` orchestration and API entry points.
- `src/ibis_profiling/cli.py`: Command-line interface.

## Proposed Solution

### 1. Update `CorrelationEngine.compute_all`
Modify `compute_all` to:
-   Accept `max_columns: int = 15`.
-   If `len(numeric_cols) > max_columns`:
    -   Sort columns based on `variables` metadata:
        -   Sort by `n_missing` (ascending).
        -   Sort by `variance` (descending).
        -   Alphabetical tie-break.
    -   Select top `max_columns`.
    -   Return a `truncated` flag or similar metadata.

### 2. Update `Profiler` and `ProfileReport`
-   Add `correlations_max_columns` to `__init__` and `profile` function.
-   In `_run_correlations`, check if the result indicates truncation and add a warning to `report.analysis["warnings"]`.

### 3. Update CLI
-   Expose `--correlations-max-columns` with a default of 15.

## Git Strategy
- **Branch:** `fix/correlations-max-columns`
- **Commits:**
  - Add correlations_max_columns to Profiler and API.
  - Implement deterministic column selection in CorrelationEngine.
  - Add warning for truncated correlations.
  - Expose parameter in CLI.
  - Add wide-table verification test.

## Phased Approach

### Phase 1: Logic Implementation
- [ ] Update `src/ibis_profiling/report/model/correlations.py`:
    - Add `max_columns` to `compute_all`.
    - Implement the sorting/selection logic.
    - Return metadata about truncation.
- [ ] Update `src/ibis_profiling/__init__.py`:
    - Add parameter to `Profiler`, `profile`, and `ProfileReport`.
    - Record warnings if truncation happened.

### Phase 2: CLI and UI
- [ ] Update `src/ibis_profiling/cli.py`:
    - Add the new option.
- [ ] Ensure the warning is clearly visible in the report.

### Phase 3: Verification
- [ ] Create `tests/test_correlations_cap.py`.
- [ ] Test with a table having 30 numeric columns and `max_columns=10`.
- [ ] Verify that the 10 "best" columns were selected.
- [ ] Verify that a warning is present in the report.

## Testing Strategy
- **Truncation Verification:** Ensure only `max_columns` are present in the final correlation matrices.
- **Selection Determinism:** Verify that the same columns are picked every time for the same input.
- **Warning Verification:** Ensure the warning message includes the original number of columns and the limit.
- **Regression:** Ensure standard correlation behavior remains unchanged for narrow tables.

