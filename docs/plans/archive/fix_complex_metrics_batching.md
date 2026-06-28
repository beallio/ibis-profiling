# Plan: Fix Complex Metrics Batching Conflict

Resolve the Ibis error "Cannot add to projection, they belong to another relation" that occurs during the complex metrics pass.

## Problem Definition
The `n_unique` (singletons) metric is implemented using `value_counts()`, which creates a new table relation. When the `QueryPlanner` hints this as a `Value`, the `Profiler` attempts to include it in a batched `aggregate()` call on the main table. Ibis rejects this because expressions from different relations cannot be mixed in a single projection/aggregation.

## Architecture Overview
The fix involves reclassifying `n_unique` as a standalone expression (using the `Table` execution hint) so it is executed independently or in parallel, rather than being batched with simple column reductions.

## Key Files & Context
- `src/ibis_profiling/planner.py`: Defines the execution hints for complex metrics.
- `src/ibis_profiling/__init__.py`: Orchestrates the execution of complex metrics based on hints.

## Proposed Solution
Update `src/ibis_profiling/planner.py`:
-   Change the execution hint for `n_unique` from `"Value"` to `"Table"`. 
-   In this context, `"Table"` acts as a hint for "standalone execution" rather than "batched execution".

## Git Strategy
- **Branch:** `fix/complex-metrics-batching`
- **Commits:**
  - Reclassify n_unique to prevent batching conflicts.
  - Add regression test for n_unique batching safety.

## Phased Approach

### Phase 1: Logic Implementation
- [ ] Modify `src/ibis_profiling/planner.py`:
    - Locate the `n_unique` plan generation.
    - Change `"Value"` to `"Table"`.

### Phase 2: Verification
- [ ] Create `tests/test_complex_metrics_batching.py`.
- [ ] Verify that `n_unique` is still correctly calculated.
- [ ] Verify that no "Batched complex metrics failed" warning is emitted in the report.
- [ ] Run the wide table test script and confirm the warning is gone.

## Testing Strategy
- **Functional Check:** Ensure `n_unique` returns correct counts for known data.
- **Warning Check:** Capture logs/warnings and assert that the batching failure warning is NOT present.
- **Regression:** Ensure other batched metrics (like `n_distinct`, if added to complex pass in future) still batch correctly if they are simple reductions.
