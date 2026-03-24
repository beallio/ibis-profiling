# Plan: Make Missing-Matrix Sampling Backend-Agnostic

Address the issue where `MissingEngine.compute` assumes that `.execute()` returns a Polars DataFrame and calls `.to_numpy()`, which is backend-dependent.

## Problem Definition
The current implementation of `MissingEngine.compute` in `src/ibis_profiling/report/model/missing.py` uses `.execute()` to fetch sampled nullity masks. Ibis returns different objects (Polars, Pandas, or PyArrow) depending on the backend and environment. The subsequent call to `.to_numpy()` might fail or behave inconsistently.

## Architecture Overview
The fix involves switching to a more consistent execution and conversion pipeline using `to_pyarrow()`, which is supported by most Ibis backends and provides a stable path to standard Python types.

## Key Files & Context
- `src/ibis_profiling/report/model/missing.py`: Contains `MissingEngine.compute` where the problematic code resides.

## Proposed Solution
Update `MissingEngine.compute` in `src/ibis_profiling/report/model/missing.py` to:
1. Replace `.execute()` with `.to_pyarrow()`.
2. Convert the resulting PyArrow Table to a list of lists (rows) using `.to_pylist()`.

## Git Strategy
- **Branch:** `fix/missing-matrix-sampling`
- **Commits:**
  - Create reproduction test.
  - Implement backend-agnostic missingness matrix calculation.
  - Verify fix with reproduction and existing tests.

## Phased Approach

### Phase 1: Infrastructure & Verification
- [x] Create `tests/reproduce_missing_matrix_issue.py` (already drafted) to reproduce the failure by mocking `execute()` to return a PyArrow Table.
- [ ] Verify that the test fails in the current state (requires exiting Plan Mode).

### Phase 2: Logic Implementation
- [ ] Update `src/ibis_profiling/report/model/missing.py`:
    - Update `MissingEngine.compute` to use `to_pyarrow()` and `to_pylist()`.
    - Ensure it handles empty samples correctly.

### Phase 3: Verification & Cleanup
- [ ] Run the reproduction test and ensure it passes.
- [ ] Run the full test suite to ensure no regressions.
- [ ] Add a test in `tests/test_missing.py` that mocks `to_pyarrow()` to ensure it works with different backend returns.
- [ ] Delete `tests/reproduce_missing_matrix_issue.py`.

## Testing Strategy
- **Reproduction Test:** Ensure `PyArrow` tables (simulated) don't break the matrix generation.
- **Regression Test:** Ensure existing Polars-based tests still work (they will now use the new path).
- **Correctness:** Verify the structure of `matrix_values` matches what the HTML template expects (list of lists of booleans).
