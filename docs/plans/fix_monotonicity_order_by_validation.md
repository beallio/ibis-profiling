# Plan: Validate Monotonicity Order By Column Existence

Address the crash when `monotonicity_order_by` is provided but refers to a non-existent column in the table schema.

## Problem Definition
In `Profiler._run_monotonicity`, `ibis.window(order_by=self.monotonicity_order_by)` is called without verifying if `self.monotonicity_order_by` exists in the table schema. If the column is missing, the run crashes.

## Architecture Overview
The fix involves:
1.  Checking if `self.monotonicity_order_by` exists in `self.table.schema()`.
2.  If missing, adding a warning to the report and skipping monotonicity checks for all numeric columns by marking them as "Skipped".

## Key Files & Context
- `src/ibis_profiling/__init__.py`: Contains `Profiler._run_monotonicity` where the validation should be added.

## Proposed Solution
Update `_run_monotonicity` in `src/ibis_profiling/__init__.py`:

```python
        numeric_cols = [c for c, s in report.variables.items() if s.get("type") == "Numeric"]
        
        # 1. Handle missing order_by parameter
        if not self.monotonicity_order_by:
            report.analysis.setdefault("warnings", []).append(
                "Skipped monotonicity checks. Monotonicity requires a deterministic 'monotonicity_order_by' column to be reliable."
            )
            for col_name in numeric_cols:
                report.add_metric(col_name, "monotonic_increasing", "Skipped")
                report.add_metric(col_name, "monotonic_decreasing", "Skipped")
            return

        # 2. Handle non-existent order_by column
        if self.monotonicity_order_by not in self.table.schema():
            report.analysis.setdefault("warnings", []).append(
                f"Skipped monotonicity checks. The requested 'monotonicity_order_by' column '{self.monotonicity_order_by}' "
                "was not found in the table schema."
            )
            for col_name in numeric_cols:
                report.add_metric(col_name, "monotonic_increasing", "Skipped")
                report.add_metric(col_name, "monotonic_decreasing", "Skipped")
            return
```

## Git Strategy
- **Branch:** `fix/monotonicity-order-by-validation`
- **Commits:**
  - Create reproduction test.
  - Implement `monotonicity_order_by` validation.
  - Verify fix with reproduction and existing tests.

## Phased Approach

### Phase 1: Infrastructure & Verification
- [x] Create `tests/reproduce_monotonicity_crash.py` to reproduce the crash.
- [ ] Verify that the test crashes in the current state.

### Phase 2: Logic Implementation
- [ ] Update `src/ibis_profiling/__init__.py`:
    - Add the check for `self.monotonicity_order_by` in `self.table.schema()`.
    - Emit a descriptive warning.
    - Mark all numeric columns as "Skipped" for monotonicity metrics.

### Phase 3: Verification & Cleanup
- [ ] Run the reproduction test and ensure it passes (no crash, warning present).
- [ ] Run the full test suite to ensure no regressions.
- [ ] Delete `tests/reproduce_monotonicity_crash.py`.

## Testing Strategy
- **Reproduction Test:** Ensure an invalid column name does not cause a crash and produces a warning.
- **Regression Test:** Ensure valid `monotonicity_order_by` still works correctly.
- **Consistency:** Verify that the "Skipped" string is used consistently with other skip cases in the project.
