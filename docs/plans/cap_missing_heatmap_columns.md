# Plan: Cap Missingness Heatmap Columns

Add a column cap for the missingness correlation heatmap to prevent $O(n^2)$ resource exhaustion on wide datasets.

## Problem Definition
The missingness heatmap computes Pearson correlations between all columns that contain at least one missing value. For wide datasets with many sparse columns, this results in an $n^2$ complexity which can cause memory blowups and slow down report generation.

## Architecture Overview
The fix involves:
1.  Adding a `missing_heatmap_max_columns` parameter to the `Profiler` and `ProfileReport` APIs (default: 15).
2.  Updating `MissingEngine.compute` to prioritize columns with the highest missing counts when truncation is necessary.
3.  Recording a warning in the report when truncation occurs.

## Key Files & Context
- `src/ibis_profiling/report/model/missing.py`: Contains `MissingEngine.compute`.
- `src/ibis_profiling/__init__.py`: `Profiler` orchestration and API entry points.
- `src/ibis_profiling/cli.py`: Command-line interface.

## Proposed Solution

### 1. Update `MissingEngine.compute`
Modify `compute` to:
-   Accept `max_heatmap_columns: int = 15`.
-   If `len(cols_with_missing) > max_heatmap_columns`:
    -   Sort `cols_with_missing` by `n_missing` descending.
    -   Select top `max_heatmap_columns`.
    -   Return truncation metadata in the `heatmap` dict.

### 2. Update `Profiler` and `ProfileReport`
-   Add `missing_heatmap_max_columns` to `__init__` and `profile` function.
-   Pass this limit to `MissingEngine.compute`.
-   In `Profiler.run`, check for truncation metadata and add a warning to `report.analysis["warnings"]`.

### 3. Update CLI
-   Expose `--missing-heatmap-max-columns` with a default of 15.

## Git Strategy
- **Branch:** `fix/cap-missing-heatmap`
- **Commits:**
  - Add missing_heatmap_max_columns to API and Profiler.
  - Implement column capping in MissingEngine.
  - Add truncation warning for missingness heatmap.
  - Expose parameter in CLI.

## Phased Approach

### Phase 1: Engine Logic
- [ ] Modify `src/ibis_profiling/report/model/missing.py`:
    - Update `compute` to accept `max_heatmap_columns`.
    - Implement sorting and truncation.
    - Include `_metadata` in heatmap output.

### Phase 2: Orchestration & API
- [ ] Update `src/ibis_profiling/__init__.py`:
    - Add parameter to `Profiler`, `profile`, and `ProfileReport`.
    - Handle warning emission.

### Phase 3: CLI
- [ ] Update `src/ibis_profiling/cli.py`.

### Phase 4: Verification
- [ ] Create `tests/test_missing_heatmap_cap.py`.
- [ ] Verify that only top-K columns are included when limit is hit.
- [ ] Verify warning presence.

## Testing Strategy
- **Truncation:** Ensure heatmap only contains the specified number of columns.
- **Priority:** Verify that columns with more missing values are kept over those with fewer.
- **Warning:** Confirm descriptive warning is added to the analysis.
- **Regression:** Ensure narrow tables still show all missing columns in the heatmap.
