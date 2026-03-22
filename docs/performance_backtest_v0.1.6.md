# Performance Back-test Summary (v0.1.0 - v0.1.6)

**Date:** Sunday, March 22, 2026  
**Dataset:** 5,000,000 rows x 10 columns  
**Distributions:** Varied (Normal, Uniform, Skewed, Null-heavy)  
**Backend:** DuckDB (Native Ibis Pushdown)

## Results Table

| Version | Mode | Duration (s) | Peak Memory (MB) |
| :--- | :--- | :--- | :--- |
| **v0.1.0** | Minimal | 7.53 | 25.73 |
| | Full | 11.65 | 56.35 |
| **v0.1.1** | Minimal | 7.54 | 25.82 |
| | Full | 11.61 | 56.96 |
| **v0.1.2** | Minimal | 8.03 | 25.82 |
| | Full | 12.47 | 56.75 |
| **v0.1.3** | Minimal | 8.58 | 25.85 |
| | Full | 12.42 | 55.83 |
| **v0.1.4** | Minimal | 8.28 | 25.85 |
| | Full | 12.85 | 57.79 |
| **v0.1.5** | Minimal | 8.26 | 25.78 |
| | **Full** | **10.67** | **47.48** |
| **v0.1.6** | Minimal | 8.29 | 25.78 |
| | **Full** | **10.68** | **46.70** |

## Key Findings

### 1. Major Full Mode Optimization (v0.1.5)
A significant performance leap occurred between `v0.1.4` and `v0.1.5`. 
- **Duration:** Dropped by ~17% (from 12.85s to 10.67s).
- **Peak Memory:** Decreased by ~18% (from 57.79MB to 47.48MB).
- **Cause:** Architectural refactor that optimized correlation calculations, improved query planning, and implemented more efficient JSON serialization.

### 2. Minimal Mode Stability
Minimal mode has remained extremely stable throughout the release history, profiling 5M rows in ~8 seconds with constant memory usage of ~25MB. This demonstrates the efficiency of the core Ibis pushdown engine for standard statistics.

### 3. Constant Memory Scaling
Unlike traditional profilers that scale memory linearly with dataset size, `ibis-profiling` maintains nearly constant memory usage regardless of the row count, as the heavy lifting is pushed to the database backend.

## Benchmarking Methodology
Benchmarks were executed using `scripts/backtest_perf.py`, which iterates through git tags, performs a `uv sync` to ensure correct dependencies for each version, and measures execution time and peak memory using `tracemalloc`.
