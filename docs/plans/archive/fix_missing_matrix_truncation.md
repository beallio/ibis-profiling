# Plan: Missingness Matrix Truncation and Warning

Add a column cap for the missingness matrix (nullity patterns) and display a warning when truncation occurs.

## Problem Definition
The missingness matrix (which shows the locations of null values) currently attempts to include all columns from the dataset. For wide datasets, this results in extremely large HTML reports and performance degradation in the browser. Furthermore, there is no UI warning when columns are excluded from this visualization.

## Architecture Overview
1.  **API Update:** Add `missing_matrix_max_columns` parameter (default: 50) to the Profiler and Report APIs.
2.  **Engine Logic:** Update `MissingEngine.compute` to truncate the `columns` list used for the matrix if it exceeds the cap.
3.  **Prioritization:** Prioritize columns with at least some missing values, then by missing count.
4.  **UI Warning:** Add a warning to the report analysis and update the HTML templates to display this warning in the "Matrix" sub-tab of the Missing values section.

## Key Files
- `src/ibis_profiling/report/model/missing.py`: Implementation of matrix capping.
- `src/ibis_profiling/__init__.py`: Orchestration and warning emission.
- `src/ibis_profiling/templates/default.html`: UI display of the warning.
- `src/ibis_profiling/templates/ydata-like.html`: UI display of the warning.

## Phased Approach

### Phase 1: Logic & API
- [ ] Update `src/ibis_profiling/report/model/missing.py`:
    - Add `max_matrix_columns` parameter to `compute`.
    - Implement truncation logic for the `matrix` output.
    - Include `_metadata` in the `matrix` dict.
- [ ] Update `src/ibis_profiling/__init__.py`:
    - Add `missing_matrix_max_columns` to all entry points.
    - Emit warning if matrix is truncated.

### Phase 2: UI Templates
- [ ] Update `default.html`: Add warning box to the matrix view.
- [ ] Update `ydata-like.html`: Add warning box to the matrix view.

### Phase 3: Verification
- [ ] Create `tests/test_missing_matrix_cap.py`.
- [ ] Run full test suite.

## Git Strategy
- **Branch:** `fix/missing-matrix-truncation`
- **Commits:**
  - Implement missingness matrix truncation in engine.
  - Add missing_matrix_max_columns to Profiler and API.
  - Update UI templates with truncation warnings.
