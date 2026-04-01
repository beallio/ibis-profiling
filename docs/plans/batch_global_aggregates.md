# Plan: Batch Global Aggregates to Avoid Oversized Queries

## Problem Definition
The current implementation of `QueryPlanner.build_global_aggregation` builds a single massive aggregation query for all columns and metrics. On wide tables (e.g., 1000+ columns), this can exceed backend SQL expression limits, lead to timeouts, or cause the entire profiling process to fail if a single column/metric fails.

## Architecture Overview
The solution involves splitting the large list of aggregate expressions into smaller batches. Each batch will be executed as a separate query, and the results will be merged horizontally into a single result set before further processing.

- **QueryPlanner**: Updated to chunk expressions and return a list of plans.
- **Profiler**: Updated to execute multiple plans and merge results using Polars.
- **Execution Engine**: Remains unchanged (executes one plan at a time).

## Core Data Structures
- `raw_results`: Now constructed by merging multiple 1-row Polars DataFrames.

## Public Interfaces
- `Profiler`: Added `global_batch_size` (default: 500) to constructor and `profile()` helper.
- `QueryPlanner`: `build_global_aggregation` now returns `list[ir.Table]`.

## Dependency Requirements
- No new dependencies (uses existing `ibis` and `polars`).

## Testing Strategy
- **Regression**: `tests/test_planner.py` will be updated to handle the new list return type.
- **Functional**: `tests/test_batch_aggregates.py` will verify that:
    - Results are identical with and without batching.
    - Batching is correctly triggered based on the threshold.
    - Wide tables (many columns) are handled correctly.
- **Performance**: Benchmark wide table profiling to ensure batching doesn't introduce significant overhead.

## Phased Approach

### Phase 1: Infrastructure & API
- [ ] Create feature branch `fix/batch-global-aggregates`.
- [ ] Update `Profiler` and `profile()` to accept `global_batch_size`.
- [ ] Update `QueryPlanner` constructor to store `global_batch_size`.

### Phase 2: Core Logic (TDD Red)
- [ ] Update `tests/test_planner.py` to expect a list (it will fail now).
- [ ] Implement batching logic in `QueryPlanner.build_global_aggregation`.
- [ ] Update `Profiler.run()` to execute and merge batch results.
- [ ] Verify `tests/test_planner.py` passes (TDD Green).

### Phase 3: Verification & Wide Table Test
- [ ] Create `tests/test_batch_aggregates.py` with a wide schema test.
- [ ] Verify identical results between batched and unbatched (if possible by setting threshold high).
- [ ] Ensure a warning is emitted when batching is used.

### Phase 4: Performance & Docs
- [ ] Run apples-to-apples benchmark on a wide table (e.g., 500 columns).
- [ ] Update `README.md` with new configuration option.
- [ ] Final regression check.

## Git Strategy
- Branch: `fix/batch-global-aggregates`
- Commit after each functional step (Infrastructure, Logic, Tests, Docs).
- Every commit must pass linting and tests.
