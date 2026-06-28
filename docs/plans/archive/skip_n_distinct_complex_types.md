# Plan: Skip n_distinct for Complex/Unhashable Types

## Problem Definition
In `QueryPlanner.build_global_aggregation`, the profiler attempts to compute `n_distinct` for all columns. However, complex types like `dt.Array`, `dt.Map`, `dt.Struct`, and `dt.JSON` often do not support `nunique` operations in various backends (including DuckDB), which can cause the entire batch aggregation to fail.

## Architecture Overview
- Update `QueryPlanner.build_global_aggregation` to include a type guard for `n_distinct`.
- Explicitly exclude complex/unhashable types from `n_distinct` calculation in the global pass.
- Ensure these columns still appear in the report with `n_distinct` as `None` or a safe default.

## Core Data Structures
No changes to data structures.

## Public Interfaces
No changes to public interfaces.

## Dependency Requirements
No new dependencies.

## Git Strategy
- Branch: `fix/skip-n-distinct-complex-types`
- Commit frequency: Incremental commits after each functional change.

## Testing Strategy
- Create `tests/test_complex_types_profiling.py`.
- Verify that profiling a table with `Array` and `Map` types doesn't crash during the global aggregation pass.
- Verify that `n_distinct` is correctly omitted for these columns.

## Phased Approach

### Phase 1: Infrastructure
- [ ] Create feature branch `fix/skip-n-distinct-complex-types`.
- [ ] Create reproduction test `tests/test_complex_types_profiling.py` (RED).

### Phase 2: Core Logic
- [ ] Implement type guard in `src/ibis_profiling/planner.py`.
- [ ] Verify tests pass (GREEN).

### Phase 3: Verification & Cleanup
- [ ] Run full test suite.
- [ ] Run apples-to-apples benchmark.
- [ ] Execute PE review.
- [ ] Submit PR and merge if benchmarks are reasonable.
