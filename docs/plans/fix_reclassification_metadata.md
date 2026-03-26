# Plan: Fix Reclassification Metadata Consistency

## Problem Definition
When `Profiler._reclassify` runs, it may change a column's type from `Numeric` to `Categorical` (e.g., low-cardinality integers). However, numeric-only metrics like `mean`, `std`, and quantiles have already been calculated and populated in the report's variable metadata by `InternalProfileReport._build()`. These numeric metrics remain in the categorical column's metadata, leading to inconsistency.

## Architecture Overview
- `Profiler._reclassify` is responsible for flipping `Numeric` columns to `Categorical` based on `cardinality_threshold`.
- This happens in the `Profiler.run()` lifecycle after the initial report object is created.

## Core Data Structures
- `InternalProfileReport.variables`: A dictionary where each key is a column name and the value is a dictionary of stats.
- `InternalProfileReport.table["types"]`: A dictionary tracking the count of each variable type.

## Proposed Changes
1.  **Logic (Infrastructure):**
    - Modify `Profiler._reclassify` in `src/ibis_profiling/__init__.py`.
    - When a column is reclassified to `Categorical`:
        - Remove numeric-only keys from its `stats` dictionary.
        - Ensure `report.table["types"]` is updated correctly.
2.  **Verification:**
    - Use `tests/reproduce_reclassification_metadata.py` to verify the fix.
    - Run full test suite.

## Dependency Requirements
- None

## Testing Strategy
- **Reproduction Test:** `tests/reproduce_reclassification_metadata.py` confirms that `mean` and other numeric metrics are absent for a reclassified categorical column.
- **Regression Test:** Run `uv run pytest tests/` to ensure no other features are broken.

## Performance Benchmarking
- **Dataset:** 100 columns x 1000 rows (all columns reclassified).
- **Baseline (dev):** 2.6116s (avg of 10 iterations)
- **Fixed (working branch):** 2.6463s (avg of 10 iterations)
- **Impact:** +1.3% (0.03s overhead for 100 columns). The overhead is negligible for report assembly.

## Task List
- [x] Task 1: Update `Profiler._reclassify` to remove numeric-only metrics.
- [x] Task 2: Update `Profiler._reclassify` to correctly update `report.table["types"]`.
- [x] Task 3: Verify fix with reproduction test.
- [x] Task 4: Run full test suite and confirm zero regressions.
- [x] Task 5: Document results.
- [x] Task 6: Perform performance benchmarking.

