# Ibis Profiling

An ultra-high-performance data profiling system built natively for **Ibis**.

## Core Principle: Profiling as Query Compilation

Unlike traditional profiling tools (e.g., `ydata-profiling`) that iterate over columns or load data into local memory (Pandas), **Ibis Profiling** treats profiling as a **query planning problem**. 

It compiles dozens of statistical metrics into a **minimal set of optimized SQL queries** that execute directly in your remote backend (DuckDB, BigQuery, Snowflake, ClickHouse, etc.). This ensures that computation happens where the data lives, enabling the profiling of multi-billion row datasets in seconds rather than hours.

## Features

- **Backend Pushdown:** 100% of the heavy lifting is done by the database engine.
- **Minimal Round-trips:** Batches all simple aggregations (mean, std, min, max, quantiles) into a single SQL pass.
- **Constant Memory Footprint:** Python only handles the final aggregated results (typically ~1 row of data), regardless of the input dataset size.
- **Semantic Parity:** Metrics and naming conventions (e.g., `n_distinct` vs `n_unique`) are aligned with industry standards and spiritual predecessors.
- **Modern Tech Stack:** Built on **Polars**, **PyArrow**, and **Ibis** for maximum internal performance and compatibility.

## Performance Benchmarks

Benchmarks were conducted using a financial loan dataset on a standard Linux environment using the **DuckDB** backend.

| Dataset Size | Ibis-Native Profiler | ydata-profiling (Minimal) | Speedup |
| :--- | :--- | :--- | :--- |
| **1 Million Rows** | **0.39 seconds** | **10.15 seconds** | **~26x Faster** |
| **5 Million Rows** | **6.66 seconds** | **40.80 seconds** | **~6x Faster** |
| **20 Million Rows** | **30.00 seconds** | **~10+ minutes (est)** | **~20x Faster** |

*Note: Ibis Profiler results include full statistics (all quantiles), while ydata-profiling was run in "minimal" mode.*

## Installation

```bash
uv add ibis-profiling
```

## Quick Start

```python
import ibis
from ibis_profiling import profile

# 1. Connect to any Ibis-supported backend
con = ibis.duckdb.connect()
table = con.read_parquet("large_dataset.parquet")

# 2. Generate the profile (Zero-memory overhead)
report = profile(table)

# 3. Access results
print(report.to_dict()) # JSON-serializable dictionary
# report.to_html() returns the HTML string for visualization
```

## Use Cases

1. **Warehouse Profiling:** Profile data directly in Snowflake or BigQuery without egressing data to local Python environments.
2. **CI/CD Data Validation:** Run lightweight profiling in automated pipelines to detect schema drift or statistical anomalies in new data partitions.
3. **Massive Parquet/CSV Analysis:** Leverage DuckDB's parallel execution to profile multi-gigabyte local files in seconds.
4. **Interactive Data Exploration:** Generate instant statistical summaries in Jupyter notebooks without waiting for row-iterative loops.

## Supported Metrics

### Dataset Metrics
- `row_count`: Total number of records.
- `n_var`: Total number of columns.
- `n_cells`: Total number of data points (n * n_var).
- `missing_cells`: Total count of nulls across all columns.

### Column Metrics (Numerical & Temporal)
- **Descriptive:** `mean`, `std`, `sum`, `variance`, `cv` (coefficient of variation).
- **Extrema:** `min`, `max`, `range`.
- **Quantiles:** `p5`, `p25`, `median` (p50), `p75`, `p95`.
- **Counts:** `missing`, `zeros`, `infinite`.
- **Uniqueness:** 
  - `n_distinct`: Number of distinct values (SQL `COUNT(DISTINCT)`).
  - `n_unique`: Number of **Singletons** (values appearing exactly once).

## Architecture

The system is decoupled into five core modules:
1. **Dataset Inspector:** Zero-execution schema analysis.
2. **Metric Registry:** Declarative metric definitions as Ibis expressions.
3. **Query Planner:** The "compiler" that batches compatible expressions into minimal plans.
4. **Execution Engine:** Dispatches compiled Ibis ASTs to the backend using PyArrow transport.
5. **Report Builder:** Aggregates and formats raw backend results into structured JSON/HTML.

## Custom Metrics

You can extend the profiler by registering your own Ibis-based metrics:

```python
from ibis_profiling.metrics import registry, Metric, MetricCategory
import ibis.expr.datatypes as dt

registry.register(Metric(
    name="my_custom_metric",
    category=MetricCategory.COLUMN,
    applies_to=[dt.Numeric],
    build_expr=lambda col: col.approx_nunique() # Use backend-specific features
))
```
