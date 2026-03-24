# Plan: Enhance Overview Metrics & Type Classification

## Problem Definition
1. The `default.html` template hardcodes variable types in the Overview box, omitting `DateTime` and any other non-standard types.
2. The `SummaryEngine` lumps complex types (Arrays, Structs, etc.) into `Categorical`, which is inaccurate.
3. Several useful dataset-level metrics (e.g., `n_vars_all_missing`, `n_distinct_rows`) are calculated but not displayed in the Overview.

## Proposed Solution
1. Update `src/ibis_profiling/report/model/summary.py` to better classify `Unsupported` and `Complex` types.
2. Update `src/ibis_profiling/templates/default.html` to dynamically render variable types or at least include `DateTime` and `Unsupported`.
3. Add missing dataset metrics to the Overview tab in `default.html`.

## Key Files & Context
- `src/ibis_profiling/report/model/summary.py`: Type mapping logic.
- `src/ibis_profiling/templates/default.html`: Overview UI.
- `src/ibis_profiling/report/report.py`: Metric calculation/serialization.

## Implementation Plan

### Phase 1: Infrastructure & Reproduction
- [ ] Create a test in `tests/test_overview_metrics.py` that checks the `table` summary for correct type counts and presence of duplication metrics.
- [ ] Create a test with `DateTime` and `Array` columns to verify type classification.

### Phase 2: Core Logic (Type Mapping)
- [ ] Refine `SummaryEngine.process_variables` to distinguish `Binary`, `Array`, `Map`, `Struct`, and `JSON` from `Categorical`.
- [ ] Use `Unsupported` as the fallback type.

### Phase 3: UI Updates
- [ ] Update `default.html` to include `DateTime` and `Unsupported` in the variables summary.
- [ ] (Optional) Make the `default.html` variables summary more dynamic to handle future types.
- [ ] Add `Duplicate Rows` count and `All Missing` variable count to the `default.html` overview.

### Phase 4: Verification
- [ ] Run the new tests.
- [ ] Run the full test suite.
- [ ] Generate a sample report and visually verify the Overview box.

## Git Strategy
- Branch: `feat/improve-overview-metrics`
- Commit frequency: After each phase.

## Task Decomposition

### Phase 1: Infrastructure & Reproduction
- **Task 1.1**: Create `tests/test_overview_metrics.py` verifying `DateTime` and `Unsupported` counts in `report.table["types"]`.
    - **Scope**: Test creation.
    - **Validation**: `./run.sh uv run pytest tests/test_overview_metrics.py`.
- **Task 1.2**: Commit the test.

### Phase 2: Logic Refinement
- **Task 2.1**: Update `src/ibis_profiling/report/model/summary.py` to handle more Ibis types.
    - **Scope**: Code modification.
    - **Validation**: Pass `tests/test_overview_metrics.py`.
- **Task 2.2**: Commit the logic changes.

### Phase 3: UI Enhancements
- **Task 3.1**: Update `src/ibis_profiling/templates/default.html` to show `DateTime` and refine the layout.
    - **Scope**: Template modification.
    - **Validation**: Visual check or string assertion in generated HTML.
- **Task 3.2**: Update `src/ibis_profiling/templates/ydata-like.html` if necessary (though it seems dynamic).
- **Task 3.3**: Commit the UI changes.

### Phase 4: Final Verification
- **Task 4.1**: Run full test suite.
- **Task 4.2**: Record session log.
