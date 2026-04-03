# Performance Benchmark Matrix

This document summarizes the performance and memory usage of `ibis-profiling` across various dataset scales and batch sizes.

## Benchmark Results (Full Profile)

| Rows | Cols | Total Cells | Batch Size | Duration (s) | Peak RSS (MB) | Status |
|------|------|-------------|------------|--------------|---------------|--------|
| 1M | 10 | 10M | 5 | 2.81 | 801.65 | Success |
| 1M | 10 | 10M | 50 | 2.61 | 798.58 | Success |
| 1M | 10 | 10M | 500 | 2.84 | 848.51 | Success |
| 1M | 50 | 50M | 5 | 11.86 | 2401.54 | Success |
| 1M | 50 | 50M | 50 | 11.42 | 2484.93 | Success |
| 1M | 50 | 50M | 500 | 11.62 | 2439.66 | Success |
| 10M | 10 | 100M | 5 | 18.59 | 1443.84 | Success |
| 10M | 10 | 100M | 50 | 18.57 | 1401.19 | Success |
| 10M | 10 | 100M | 500 | 19.18 | 1347.39 | Success |
| 10M | 50 | 500M | 5 | 88.01 | 2640.57 | Success |
| 10M | 50 | 500M | 50 | 84.50 | 2877.66 | Success |
| 10M | 50 | 500M | 500 | 89.41 | 3610.29 | Success |

## Key Takeaways

1. **Batching Impact on Memory:** Reducing the `global_batch_size` significantly stabilizes memory usage on wide and large datasets. For a 500M cell dataset, reducing the batch size from 500 to 50 saved ~730MB of peak RSS.
2. **Throughput Efficiency:** Small batches have minimal impact on total profiling duration (often < 5% difference), making them a safe and effective default for large data.
3. **Advanced Pass Stability:** Batching the Skewness/MAD calculations (the "Advanced Pass") prevented OOMs that were previously occurring on 20M+ row datasets.

## Memory Heuristics

The `MemoryManager` now automatically applies the following logic:

- **Dynamic Batch Size:** 
    - `< 10M cells`: 500 (Priority: Speed)
    - `< 100M cells`: 100
    - `< 500M cells`: 50
    - `> 500M cells`: 20 (Priority: Safety)
- **Automatic Memory Limit:** Automatically detects available system RAM and sets DuckDB's `memory_limit` to **70% of free memory**.
