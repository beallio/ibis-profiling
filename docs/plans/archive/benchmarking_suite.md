# Plan: Optimized Benchmarking Suite for ibis-profiling vs ydata-profiling

## Problem Definition
`ydata-profiling` is extremely slow and memory-intensive on large datasets. We need an optimized benchmarking strategy that balances depth (full profiling on small data) with breadth (minimal profiling on large data) and ensures system stability through aggressive memory management.

## Architecture Overview
The suite remains composed of a data generator, a benchmark runner, and a parity checker. The runner will be updated with sophisticated scheduling and cleanup logic.

## Implementation Plan

### Phase 1: Updated Data Generation
-   Modify `scripts/run_benchmarks.py` to support the new size list: `[10_000, 25_000, 50_000, 500_000, 1_000_000, 5_000_000, 10_000_000, 20_000_000]`.

### Phase 2: Optimized Benchmark Runner
-   **Profiling Logic**:
    *   Sizes < 500k (10k, 25k, 50k): Run both **Minimal** and **Full** profiling.
    *   Sizes >= 500k: Run **only Minimal** profiling.
-   **Memory Management**:
    *   Explicitly call `gc.collect()` between runs.
    *   Delete large dataframes/tables after each benchmark iteration.
    *   Use `tracemalloc` to continue tracking peak memory.
-   **Output**: Save results to `/tmp/ibis-profiling/benchmarks/results.json`.

### Phase 3: Parity Comparison
-   Run `scripts/compare_outputs.py` on the 50k dataset (Full mode) to ensure statistical parity on a complex but manageable size.

### Phase 4: Documentation
-   Update `README.md` with the new performance metrics.
-   Highlight the "Full vs Minimal" transition in the results table.

## Verification
-   Ensure all sizes are generated and profiled correctly.
-   Verify that `ydata` is only run in minimal mode for large datasets.
-   Confirm memory usage stays within reasonable bounds.
