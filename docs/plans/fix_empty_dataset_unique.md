# Plan: Fix is_unique for empty datasets

## Problem Definition
When `n == 0`, `is_unique` is currently set to `True` because `n_distinct == n` (0 == 0). This incorrectly marks empty datasets as unique.

## Architecture Overview
The fix involves modifying `ProfileReport._build` in `src/ibis_profiling/report/report.py` to correctly handle the `n == 0` case for the `is_unique` metric.

## Phased Approach

### Phase 1: Infrastructure & Reproduction
- [x] Create reproduction test `tests/reproduce_empty_dataset_unique.py`.
- [x] Verify that `is_unique` is `True` for an empty table.
- [x] Create a new feature branch `fix/empty-dataset-unique`.

### Phase 2: Implementation
- [x] Modify `src/ibis_profiling/report/report.py` to set `is_unique = False` (or `None`) when `n == 0`.
- [x] Ensure `n_distinct == n` check only applies when `n > 0`.

### Phase 3: Verification
- [x] Run reproduction test and verify it passes with the fix.
- [x] Run full test suite to ensure no regressions.
- [x] Update session log.

## Git Strategy
- Branch: `fix/empty-dataset-unique`
- Commits:
  - Fix is_unique logic for empty datasets in report builder.
  - Add test case for empty dataset uniqueness.

## Testing Strategy
- A new test file `tests/reproduce_empty_dataset_unique.py` will:
    - Create an empty Ibis table.
    - Run the profiler.
    - Assert that `is_unique` for all columns is `False`.
