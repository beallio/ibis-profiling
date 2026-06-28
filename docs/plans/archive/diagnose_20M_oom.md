# Plan: Diagnose OOM in 20M x 10cols Dataset

## Objective
Identify the specific profiling phase or operation causing Out-Of-Memory (OOM) errors when profiling a 20-million-row, 10-column dataset.

## Key Files & Context
- **Diagnostic Script:** `scripts/diagnose_20M_10cols.py` (to be created)
- **Library Code:** `src/ibis_profiling/profiler.py`, `src/ibis_profiling/engine.py`
- **Data:** `/tmp/ibis-profiling/data_20M_empty_10cols.parquet`

## Implementation Steps

### 1. Create Diagnostic Script
Create `scripts/diagnose_20M_10cols.py` that:
- Generates 20M rows x 10 columns (if not already present).
- Uses `psutil` to log RSS memory usage before and after each major profiling phase.
- Hooks into the `on_progress` callback to provide fine-grained memory tracking.
- Runs `ProfileReport(table, minimal=False, parallel=False)` to isolate the cause.

### 2. Execute and Monitor
Run the diagnostic script:
```bash
export VIRTUAL_ENV=/tmp/ibis-profiling/.venv
$VIRTUAL_ENV/bin/python scripts/diagnose_20M_10cols.py
```
Observe the logs to see where the process is killed (look for the last logged phase).

### 3. Analyze and Propose Fix
Based on the failure point:
- If **Global Aggregates** fail: Investigate batching or DuckDB memory limits.
- If **Advanced Pass (Histograms)** fail: Investigate `to_pyarrow().to_pydict()` on large histogram results.
- If **Complex Pass (n_unique)** fail: Investigate the `n_unique_threshold` effectiveness.
- If **Correlations** fail: Investigate sampling logic.

## Verification & Testing
- The "fix" will be verified by successfully running the 20M profiling with the proposed optimizations.
