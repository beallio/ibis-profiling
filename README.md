# Ibis Profiling

An ultra-high-performance data profiling system built natively for **Ibis**.

## Core Principle: Profiling as Query Compilation

Unlike traditional profiling tools (e.g., `ydata-profiling`) that iterate over columns or load data into local memory (Pandas), **Ibis Profiling** treats profiling as a **query planning problem**. 

It compiles dozens of statistical metrics into a **minimal set of optimized SQL queries** that execute directly in your remote backend (DuckDB, BigQuery, Snowflake, ClickHouse, etc.). This ensures that computation happens where the data lives, enabling the profiling of multi-billion row datasets in seconds rather than hours.

## Features

- **Backend Pushdown:** 100% of the heavy lifting is done by the database engine.
- **Minimal Round-trips:** Batches all simple aggregations (mean, std, min, max, quantiles) into a single SQL pass.
- **Constant Memory Footprint:** Python only handles the final aggregated results (typically ~1 row of data), regardless of the input dataset size.
- **ydata-profiling Drop-in API:** Includes a `ProfileReport` class that mimics the standard ydata API for easy migration.
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

## Quick Start (ydata-style)

```python
import ibis
from ibis_profiling import ProfileReport

# 1. Connect to any Ibis-supported backend
con = ibis.duckdb.connect()
table = con.read_parquet("large_dataset.parquet")

# 2. Generate the profile (Zero-memory overhead)
report = ProfileReport(table)

# 3. Access or export results
report.to_file("report.html")
report.to_file("report.json")
stats = report.get_description()
```

## Use Cases & Examples

### 1. Warehouse Profiling (BigQuery / Snowflake)
Profile data directly in your cloud warehouse without egressing rows to your local machine.

```python
import ibis
from ibis_profiling import ProfileReport

# Connect to Snowflake
con = ibis.snowflake.connect(...)
table = con.table("massive_events_table")

# Computation happens remotely in Snowflake
report = ProfileReport(table)
report.to_file("snowflake_profile.html")
```

### 2. CI/CD Data Validation
Detect schema drift or statistical anomalies in automated pipelines.

```python
def test_data_quality():
    table = ibis.read_parquet("new_partition.parquet")
    report = ProfileReport(table).to_dict()
    
    # Assert no missing values in critical columns
    assert report["columns"]["user_id"]["missing"] == 0
    # Assert mean transaction value is within normal bounds
    assert 10 < report["columns"]["amount"]["mean"] < 500
```

### 3. Massive Local File Analysis
Leverage DuckDB's parallel engine to profile multi-gigabyte local files.

```python
import ibis
from ibis_profiling import ProfileReport

# DuckDB handles the heavy lifting
table = ibis.read_parquet("20GB_data.parquet")
report = ProfileReport(table)
print(f"Total Rows: {report.to_dict()['dataset']['row_count']}")
```

### 4. Synthetic Data Generation
Generate high-volume test data using the included CLI/Script.

```bash
# Generate 1 million rows of fake loan data for testing
uv run scripts/generate_test_data.py --type loan --rows 1000000 --output /tmp/test_data.parquet
```

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
