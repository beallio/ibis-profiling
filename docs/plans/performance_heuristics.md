# Plan: Exhaustive Performance Benchmarking & Memory Heuristics

## Objective
Systematically test the `ibis-profiling` engine across varied dataset scales to determine the relationship between data volume, batch size, and memory consumption. Use these findings to implement an automated heuristic for `global_batch_size` and DuckDB `memory_limit`.

## Key Files & Context
- **Benchmarking Suite:** 
    - `scripts/generate_bench_data_varied.py` (Data generation)
    - `scripts/benchmark_runner.py` (Orchestrator)
    - `scripts/benchmark_worker.py` (Individual profiling process)
- **Library Code:** `src/ibis_profiling/profiler.py`, `src/ibis_profiling/planner.py`
- **Output:** `docs/performance_benchmark_matrix.md`

## Implementation Steps

### 1. Develop Varied Data Generation Script
Create `scripts/generate_bench_data_varied.py`:
- Generates datasets with a mix of types (Integer, Float, String, Boolean, DateTime).
- **Mandatory Features:** 
    - Injects nulls (at varying rates).
    - Injects empty strings (`""`) in varchar columns.
    - Scales from 1M to 20M rows and 10 to 100 columns.
- Data will be saved as Parquet in `/tmp/ibis-profiling/bench/` to be reused across benchmark runs.

### 2. Develop Comprehensive Benchmarking Suite
Create `scripts/benchmark_runner.py` to orchestrate tests across:
- **Rows:** 1M, 5M, 10M, 20M
- **Columns:** 10, 20, 50, 100
- **Batch Sizes:** 5, 20, 50, 100, 500
- **Isolation:** Each test case runs in a **separate subprocess** (`scripts/benchmark_worker.py`) to eliminate memory pollution from generation or previous runs.

### 3. Analyze Performance & Throughput
Measure not just memory safety, but **speed**:
- Does smaller batching (`global_batch_size=5`) increase total time due to coordination overhead?
- Does massive batching (`global_batch_size=500`) cause DuckDB to slow down due to memory spilling/swapping?
- Identify the "Sweet Spot" where `Total Duration` is minimized without triggering OOM.

### 4. Derive and Implement Heuristic
Analyze results to find thresholds:
- **Heuristic Target:** `global_batch_size` and `memory_limit` should scale dynamically based on `(Rows * Columns)` and `AvailableSystemRAM`.
- Update `src/ibis_profiling/profiler.py`:
    - Implement `_calculate_optimal_batch_size()` to choose the most efficient (fastest) batch size that fits in the safety margin.
    - Set DuckDB `memory_limit` automatically.

## Verification & Testing
- **Validation:** Run the 20M x 100cols test with the new heuristic and verify stability and performance.
- **Regression:** Ensure small datasets (1M rows) still run at peak speed by defaulting to larger batches when safe.
- **Documentation:** Publish results to `docs/performance_benchmark_matrix.md`.
