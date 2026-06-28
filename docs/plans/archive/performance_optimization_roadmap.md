# Plan: Performance Optimization Roadmap

## Current State (v0.1.14-dev)
- **Benchmark:** 10M rows x 20 cols in **44.50s** (~4.4s / 1M rows).
- **Improvements:** SQL-level sanitization, optional cardinality sketches for DuckDB.

## Phased Approach & Performance Gates

### Phase 0: Baseline Establishment
- [x] Run `scripts/run_financial_benchmark.py` on current `dev`.
- [x] Save result as `baseline_v0.1.14.txt` (Result: 46.49s).

### Phase 1: Thread-Local Connections (Strategy 1)
- [x] Implement `ConnectionPool` logic in `Profiler` to allow safe `parallel=True` on DuckDB.
- [x] Benchmark with `parallel=True`.
- [x] **Gate:** Failed. Deadlocks/contention on in-memory DuckDB tables. **Reverted and Skipped**.

### Phase 2: SQL-Level Sanitization (Strategy 2)
- [x] Refactor `CorrelationEngine` and `MissingEngine` to push `isfinite` checks into Ibis expressions.
- [x] Remove Python-side sanitization loops.
- [x] Benchmark. (Result: 45.80s).
- [x] **Gate:** Passed. Shaved ~0.7s off baseline.

### Phase 3: Cardinality Sketches (Strategy 4)
- [x] Use `approx_count_distinct()` for DuckDB backends during Phase 1 aggregation.
- [x] Benchmark. (Result: 44.50s).
- [x] **Gate:** Passed. Total improvement of ~2s (4.3%) on financial dataset.

## Git Strategy
- Branch: `dev`
- Commits:
    - Optimize correlation matrix sanitization.
    - Implement optional cardinality sketches for DuckDB.

## Testing Strategy
- Ensure `tests/test_parallel_safety.py` and `tests/test_correlation_zero_variance.py` continue to pass.
- Verify accuracy of sketches vs exact counts.
