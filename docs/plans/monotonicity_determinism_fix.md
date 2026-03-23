# Plan: Monotonicity Determinism Fix

## Problem Definition
The monotonicity check in `src/ibis_profiling/__init__.py` uses `ibis.window()` without an explicit `order_by`. In many SQL backends (like DuckDB or Snowflake), the result of `lag()` over an unordered window is nondeterministic. This can lead to incorrect or inconsistent monotonicity results.

## Architecture Overview
We will modify the `_run_monotonicity` method in `src/ibis_profiling/__init__.py` to:
1.  Require `monotonicity_order_by` for the check to run.
2.  If `monotonicity_order_by` is missing, skip the check.
3.  Add a clear warning/alert to the report explaining why it was skipped.
4.  Optionally allow the user to acknowledge the risk (but by default, we prioritize safety).

## Core Data Structures
No changes to public data structures. The `variables` dictionary for numeric columns will contain `"Skipped"` for `monotonic_increasing` and `monotonic_decreasing` if no ordering is provided.

## Public Interfaces
- **`profile()` and `ProfileReport()`**: Keep `monotonicity_order_by` but change logic to require it.
- **CLI**: Already has `--monotonicity-order-by`.

## Dependency Requirements
- `ibis-framework`
- `pytest`

## Phased Implementation Plan

### Phase 1: Infrastructure & Verification (TDD)
- **Task 1.1: Create failing test for nondeterministic behavior**
    - **Scope**: Create `tests/test_monotonicity_determinism.py` that asserts "Skipped" when no order is provided.
    - **Inputs**: None
    - **Outputs**: `tests/test_monotonicity_determinism.py`
    - **Validation**: `./run.sh uv run pytest tests/test_monotonicity_determinism.py` (should fail until implemented)

### Phase 2: Core Logic Implementation
- **Task 2.1: Update `_run_monotonicity` logic**
    - **Scope**: Modify `src/ibis_profiling/__init__.py` to skip monotonicity if `self.monotonicity_order_by` is `None`.
    - **Inputs**: `src/ibis_profiling/__init__.py`
    - **Outputs**: Updated `Profiler._run_monotonicity` method.
    - **Validation**: Pass Task 1.1 test.

- **Task 2.2: Add Determinism Warning**
    - **Scope**: Add a specific warning to `report.analysis["warnings"]` when monotonicity is skipped due to missing order.
    - **Inputs**: `src/ibis_profiling/__init__.py`
    - **Outputs**: Updated warning list in the report.
    - **Validation**: Verify warning string in `tests/test_monotonicity_determinism.py`.

### Phase 3: UI & Downstream Integrity
- **Task 3.1: Verify Template Rendering**
    - **Scope**: Ensure `default.html` and `ydata-like.html` handle "Skipped" values gracefully for monotonicity fields.
    - **Inputs**: `src/ibis_profiling/templates/`
    - **Outputs**: Verified templates.
    - **Validation**: Run `tests/test_monotonicity_fixes.py` which already checks HTML output.

### Phase 4: Documentation & Finalization
- **Task 4.1: Update README.md**
    - **Scope**: Update `monotonicity_order_by` description to emphasize it is REQUIRED for determinism.
    - **Inputs**: `README.md`
    - **Outputs**: Updated documentation.
    - **Validation**: Manual review.

- **Task 4.2: Session Log**
    - **Scope**: Record results in `docs/agent_conversations/`.
    - **Inputs**: Execution results.
    - **Outputs**: JSON session log.

## Git Strategy
- **Branch**: `fix/monotonicity-determinism`
- **Commit Frequency**: After each task (1.1, 2.1, 2.2, 3.1, 4.1).
- **Commit Messages**: Imperative (e.g., "Require order_by for monotonicity checks").

## Performance Impact
Positive. Skipping window functions on unordered data avoids unnecessary full-table scans and shuffles on large datasets.

## Tool Strategy
- **Use ./run.sh**: Use ./run.sh before executing any command to ensure the correct environment variables are loaded.
- **Temp file storage**: Ensure are temporary, and ephermal files are stored in /tmp/ibis-profiling
