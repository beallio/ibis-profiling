# Plan: Remove Unused Per-Column Count Aggregation

## Problem Definition
`QueryPlanner.build_global_aggregation` includes `col.count()` for every column, resulting in `__n` metrics in the raw results. However, `ProfileReport` overwrites the per-column `n` with the dataset-wide row count. These redundant aggregates increase SQL complexity and slow down wide tables without providing any utility.

## Architecture Overview
1.  **Planner Refactor**: Remove the per-column `count()` expression from the global aggregation pass.
2.  **Summary Engine**: Ensure `SummaryEngine` correctly initializes `n` and `count` fields, which will be populated by the dataset-wide count in the report builder.
3.  **Correctness**: Verify that `n` and `count` (non-null count) remain accurate in the final report by deriving them from `dataset_n - n_missing`.

## Core Data Structures
No changes to data structures.

## Public Interfaces
No changes to public interfaces.

## Phased Approach

### Phase 1: Implementation
- [ ] Remove `col.count()` from `src/ibis_profiling/planner.py`.
- [ ] Verify `src/ibis_profiling/report/model/summary.py` handles the absence of `__n` (it should just fall through the mapping logic).

### Phase 2: Verification
- [ ] Create `tests/test_remove_column_n.py`.
- [ ] Assert that no columns ending in `__n` exist in the raw results dataframe.
- [ ] Assert that `ProfileReport.table['n']` and `ProfileReport.variables[col]['n']` are correct.
- [ ] Run full test suite.

## Git Strategy
- Branch: `refactor/remove-column-n`
- Commits:
    - `refactor: remove redundant per-column count aggregates`
