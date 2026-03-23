# Fix Dangerous Monotonicity Checks

**Background & Motivation:**
The `_run_monotonicity` method uses `ibis.window()` (a global window) without an explicit `order_by`. On large datasets, this forces backends to move all data into a single partition, leading to OOM or extreme latency. Furthermore, monotonicity is often only meaningful relative to a specific sequence (e.g., time or ID).

**Scope & Impact:**
- `src/ibis_profiling/__init__.py`: Update `Profiler` and `profile` to support `monotonicity_threshold` and `monotonicity_order_by`.
- `src/ibis_profiling/cli.py`: Expose these new parameters to the CLI.
- `tests/test_monotonicity_fixes.py`: Add new tests to verify threshold behavior and ordered windowing.

**Phased Implementation Plan:**

### Stage 1: Core Logic Update
**Changes:**
1.  **`src/ibis_profiling/__init__.py`**: 
    - Add `monotonicity_threshold: int = 100_000` to `Profiler.__init__` and `profile()`.
    - Add `monotonicity_order_by: str | None = None` to `Profiler.__init__` and `profile()`.
    - Update `_run_monotonicity`:
        - If `row_count > monotonicity_threshold` and `monotonicity` was not explicitly `True`, skip the check and add a warning.
        - If `monotonicity_order_by` is provided, use it in the window: `ibis.window(order_by=self.monotonicity_order_by)`.
        - Ensure it handles the case where the table is not ordered.
2.  **`src/ibis_profiling/cli.py`**:
    - Add `--monotonicity-threshold` (default 100,000).
    - Add `--monotonicity-order-by` (string).

### Stage 2: Verification
**Changes:**
1.  Create `tests/test_monotonicity_fixes.py`:
    - Test that monotonicity is skipped for large tables by default.
    - Test that monotonicity can be forced for large tables.
    - Test that `monotonicity_order_by` correctly influences the results (e.g., a column that is monotonic only when ordered by another).

**Verification:**
- Run `uv run pytest tests/test_monotonicity_fixes.py`.
- Run `uv run pytest tests/test_advanced_features.py` to ensure no regressions.
