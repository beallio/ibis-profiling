# Plan: Harden value_counts Planning for High-Cardinality or Unknown Stats

## Problem Definition
The current skip guard for `n_unique` and `top_values` requires both `n_total` and `n_distinct` to be present and greater than the threshold. If `n_distinct` is missing or zero (unknown), we might incorrectly run expensive `value_counts` on huge columns. Additionally, `dt.JSON` should be excluded from hashable checks.

## Architecture Overview
- Update `QueryPlanner.build_complex_metrics` to treat missing/non-numeric `n_distinct` as unknown.
- Skip `n_unique`/`top_values` if `n_total` exceeds the threshold and `n_distinct` is unknown.
- Extend `is_hashable` to exclude `dt.JSON`.

## Core Data Structures
No changes to data structures.

## Public Interfaces
No changes to public interfaces.

## Dependency Requirements
No new dependencies.

## Git Strategy
- Branch: `fix/harden-value-counts-planning`
- Commit frequency: Incremental commits after each functional change.

## Testing Strategy
- Create `tests/test_harden_planner.py`.
- Verify skip logic when `n_distinct` is missing/zero but `n_total` is large.
- Verify that `dt.JSON` is treated as non-hashable.

## Phased Approach

### Phase 1: Infrastructure
- [x] Create feature branch `fix/harden-value-counts-planning`.
- [x] Create reproduction test `tests/test_harden_planner.py` (RED).

### Phase 2: Core Logic
- [x] Update `is_hashable` logic in `src/ibis_profiling/planner.py`.
- [x] Update skip guard logic in `src/ibis_profiling/planner.py`.
- [x] Verify tests pass (GREEN).

### Phase 3: Verification & Cleanup
- [ ] Run full test suite.
- [ ] Run apples-to-apples benchmark.
- [ ] Execute PE review.
- [ ] Submit PR and merge if benchmarks are reasonable.
