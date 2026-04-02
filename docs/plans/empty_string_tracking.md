# Plan: Empty String Tracking and Alerting

## Problem Definition
Currently, empty strings (`""`) are treated as valid categorical data. They do not trigger missingness alerts, and in the UI, they appear as empty labels in frequency tables, making them difficult for users to distinguish from other data or identify as a quality issue.

## Architecture Overview
1.  **New Metric**: Introduce `n_empty` to the `MetricRegistry` to count exact empty strings in `dt.String` columns.
2.  **Aggregation**: Include `n_empty` in the global aggregation pass of the `QueryPlanner`.
3.  **Model Mapping**: Map `n_empty` in `SummaryEngine` and calculate `p_empty` in `ProfileReport.finalize()`.
4.  **Alerting**: Add a new `EMPTY` alert type to `AlertEngine` that triggers when a column has a significant percentage of empty strings.
5.  **UI/UX**: 
    *   Show "Empty" count in the variable overview.
    *   Semantically label `""` as `(Empty)` in frequency tables and histograms.

## Core Data Structures
- `stats["n_empty"]`: Count of empty strings.
- `stats["p_empty"]`: Percentage of empty strings.
- `AlertEngine`: New alert type `EMPTY`.

## Public Interfaces
No changes to public interfaces. CLI will automatically include the new metric.

## Phased Approach

### Phase 1: Core Metrics & Logic
- [ ] **t1**: Add `n_empty` metric to `src/ibis_profiling/metrics.py`.
- [ ] **t2**: Ensure `SummaryEngine` in `src/ibis_profiling/report/model/summary.py` maps `n_empty`.
- [ ] **t3**: Update `ProfileReport.finalize()` in `src/ibis_profiling/report/report.py` to calculate `p_empty` and accumulate dataset-wide empty stats (optional, but good for overview).
- [ ] **t4**: Implement `EMPTY` alert in `src/ibis_profiling/report/model/alerts.py`.

### Phase 2: UI & Downstream Integrity
- [ ] **t5**: Update `ProfileReport.add_metric()` in `src/ibis_profiling/report/report.py` to map `""` to `(Empty)` for `top_values` (Frequency Table).
- [ ] **t6**: (Optional) Update HTML templates if necessary to display the `n_empty` count in the Overview sidebar. (Note: Most categorical metrics are rendered dynamically from the `variables` dict).

### Phase 3: Verification
- [ ] **t7**: Create `tests/test_empty_strings.py` with a dataset containing mixtures of NULLs, empty strings, and valid data.
- [ ] **t8**: Verify that `n_empty` and `n_missing` are distinct and accurate.
- [ ] **t9**: Verify the `EMPTY` alert triggers at the correct threshold.
- [ ] **t10**: Run full test suite and Principal Engineer review.

## Git Strategy
- Branch: `feat/empty-string-tracking`
- Commits:
    - `feat: add n_empty metric and mapping`
    - `feat: implement EMPTY alert logic`
    - `ui: semantically label empty strings in reports`
