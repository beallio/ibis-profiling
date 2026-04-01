# Plan: Compute Pearson Correlations Once Per Pair

## Problem Definition
Pearson correlation currently builds expressions for both `(i, j)` and `(j, i)`, which doubles the aggregate work and the resulting SQL size. This slows down correlation computation and affects the missingness heatmap as well.

## Architecture Overview
The solution involves modifying the Pearson correlation calculation to compute only the upper triangle (`i < j`) of the correlation matrix. The results will then be mirrored into the lower triangle, and the diagonal will be set to 1.0.

- **CorrelationEngine**: Updated `_compute_pearson` to only generate expressions for `i < j`.
- **CorrelationEngine**: Updated `compute_all` to mirror results.
- **MissingEngine**: Updated `compute` to mirror results.

## Core Data Structures
- Correlation matrices (list of lists) remain unchanged in the final output.

## Public Interfaces
- No changes to public interfaces.

## Dependency Requirements
- No new dependencies.

## Testing Strategy
- **Functional**: `tests/test_correlation_optimization.py` will verify that:
    - The correlation matrix is symmetric.
    - The diagonal is 1.0.
    - All pairwise correlations are present and correct.
- **Regression**: Existing correlation tests must pass.

## Phased Approach

### Phase 1: Infrastructure & API
- [x] Create feature branch `fix/optimize-pearson-correlation`.
- [x] Create `tests/test_correlation_optimization.py`.

### Phase 2: Core Logic (Optimization)
- [x] Update `CorrelationEngine._compute_pearson` to compute only `i < j`.
- [x] Update `CorrelationEngine.compute_all` to mirror Pearson results.
- [x] Update `MissingEngine.compute` to mirror heatmap results.
- [x] Verify `tests/test_correlation_optimization.py` passes.

### Phase 3: Verification & Cleanup
- [x] Run full test suite.
- [x] Run apples-to-apples benchmark.
- [x] Execute PE review.
- [ ] Submit PR and merge if benchmarks are reasonable.

## Git Strategy
- Branch: `fix/optimize-pearson-correlation`
- Commit after each functional step.
