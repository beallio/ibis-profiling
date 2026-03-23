# Ibis Profiling Benchmarking Protocol

This document defines the mandatory methodology for measuring and verifying performance across releases of `ibis-profiling`.

## 1. Core Objectives
*   **Latency**: Measure end-to-end execution time for `to_json()` (the primary computation trigger).
*   **Memory**: Track peak resident set size (RSS) using `tracemalloc`.
*   **Scalability**: Verify the impact of the "N-Query" batching pass on high-column datasets.
*   **Regression Detection**: Ensure new features do not silently degrade core performance.

## 2. Standard Benchmarking Datasets
Benchmarks must be run on the following synthetic datasets (generated via `scripts/generate_bench_data.py`):

1.  **Standard Test**: 1,000,000 rows x 20 columns.
    *   *Focus*: Baseline performance for common analysis tasks.
2.  **Scalability Test**: 100,000 rows x 100 columns.
    *   *Focus*: Verifying query batching efficiency and interaction truncation.
3.  **Big Data Test**: 20,000,000 rows x 5 columns.
    *   *Focus*: Verifying sampling logic and backend stability.

## 3. Execution Methodology
*   **Environment Control**: All benchmarks must be run via `./run.sh` to ensure consistent environment variables and cache redirection to `/tmp/`.
*   **Isolation**: No other heavy processes should be running on the host during measurement.
*   **Cold Start**: The first run of any benchmark should be discarded to avoid bias from file system caching or JIT compilation.
*   **Backtesting**: Use `scripts/quick_backtest.py` to perform side-by-side comparisons with previous Git tags.

## 4. Benchmark Running Instructions

### Scenario A: Standard Local Benchmark
To measure the performance of your current local changes:
```bash
./run.sh uv run scripts/standard_benchmark.py
```

### Scenario B: Scalability Backtest (vs. Last Release)
To compare the current `dev` branch against the latest release (`v0.1.6`):
1.  Ensure the worktree is clean or stashed.
2.  Run the backtest script:
```bash
./run.sh uv run scripts/quick_backtest.py
```
*Note: This script will automatically stash your changes, checkout the release tag, perform measurements, and then restore your dev state.*

### Scenario C: Generating New Release Metrics
When preparing a new release (e.g., `v0.1.8`):
1.  Generate the full backtest report across all historical tags:
```bash
./run.sh uv run scripts/backtest_perf.py
```
2.  Review the JSON output in `/tmp/ibis-profiling/backtest_results.json`.
3.  Update `docs/performance_backtest_vX.X.X.md` with the new data.

## 5. Performance Thresholds
Any PR that increases execution time by > 10% on the **Scalability Test** must include a technical justification in the PR description.
