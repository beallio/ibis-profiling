# Plan: fix: Use backend-agnostic conversion for histogram results

## Objective
The current histogram processing logic in `Profiler._run_advanced_pass` assumes that `plan.execute()` returns a pandas-like DataFrame with a `.columns` attribute. This is not guaranteed across all Ibis backends. Switching to `to_pyarrow().to_pydict()` provides a more consistent, backend-agnostic way to handle results.

## Key Files & Context
- `src/ibis_profiling/__init__.py`: The `Profiler._run_advanced_pass` method, specifically the loop that processes `histogram_plans` results.
- `tests/test_histogram_backend_agnostic.py`: New test to verify histogram generation on multiple backends.

## Implementation Steps

### Phase 1: Infrastructure & Verification
1.  **Create a reproduction/verification test**: `tests/test_histogram_backend_agnostic.py`.
2.  **Confirm current behavior**: Run the test using `./run.sh uv run pytest tests/test_histogram_backend_agnostic.py`.

### Phase 2: Logic Change
1.  **Modify `Profiler._run_advanced_pass`**:
    - Update `run_hist` function within `_run_advanced_pass` to return the result of `plan.to_pyarrow().to_pydict()` instead of `plan.execute()`.
    - Update the result processing loop to use keys from the dictionary instead of `.columns` and pandas-style indexing.

### Phase 3: Final Verification
1.  **Run targeted tests**: Confirm the new tests pass.
2.  **Run full test suite**: Ensure no regressions.
3.  **Linting & Formatting**: Run `ruff`.

## Git Strategy
- **Branch**: `fix/histogram-backend-agnostic`
- **Commits**:
    1.  Add verification tests for backend-agnostic histograms.
    2.  Use to_pyarrow().to_pydict() for histogram result handling.
    3.  Finalize documentation and session log.
