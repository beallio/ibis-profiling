# Ibis Profiling

A data profiling system built natively for **Ibis**.

## Core Principle

This profiler treats profiling as a **query planning problem**, not a collection of Python functions. It compiles statistical metrics into a minimal set of optimal, batched queries that execute directly in the remote backend (DuckDB, BigQuery, Snowflake, etc.).

## Features

- **Minimal Query Count:** Batches dozens of metrics into a single aggregation query.
- **Backend Pushdown:** Computation happens in the database, not in Python memory.
- **Lazy Execution:** Builds expression graphs that can be inspected before execution.
- **Extensible:** Easily register custom metrics as Ibis expressions.

## Installation

```bash
uv add ibis-profiling
```

## Usage

```python
import ibis
from ibis_profiling import profile

# Connect to any Ibis-supported backend
con = ibis.duckdb.connect()
table = con.table("my_large_dataset")

# Generate the profile
report = profile(table)

import json
print(json.dumps(report, indent=2))
```

## Architecture

1. **Dataset Inspector:** Analyzes schema.
2. **Metric Registry:** Stores metric definitions as Ibis expressions.
3. **Query Planner:** Compiles metrics into a single `aggregate()` plan.
4. **Execution Engine:** Runs the plan on the backend.
5. **Report Builder:** Formats results into a structured report.
