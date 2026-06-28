# Plan: Guard correlation calculations against zero-variance columns

## Problem Definition
Pearson and Spearman correlation calculations currently divide by the product of standard deviations without checking if they are zero. This leads to NaN values in the correlation matrices for constant or all-null columns, which pollutes the final report.

## Architecture Overview
The fix involves:
1.  Modifying `src/ibis_profiling/report/model/correlations.py` to guard the denominator in correlation expressions.
2.  Using Ibis `nullif` to avoid division by zero.
3.  Sanitizing the final aggregated results to replace any accidental NaN/Inf with `None`.

## Phased Approach

### Phase 1: Implementation
- [x] Implement denominator guard in `CorrelationEngine._compute_pearson`.
- [x] Implement denominator guard in `CorrelationEngine.compute_all` (Spearman pass).
- [x] Implement result sanitization loop in `CorrelationEngine.compute_all`.

### Phase 2: Verification (TDD)
- [x] Create `tests/test_correlation_zero_variance.py` with constant and all-null columns.
- [x] Verify that reproduction test `tests/reproduce_correlation_zero_variance.py` passes (no NaNs).
- [x] Run the full test suite.

### Phase 3: Documentation
- [x] Update session log.

## Git Strategy
- Branch: `fix/correlation-zero-variance`
- Commits:
    - Guard correlation denominators against zero variance.
    - Sanitize correlation matrices for NaN/Inf.

## Testing Strategy
- The test suite will verify:
    - Constant columns have `None` or 0 correlation with others (excluding diagonal).
    - All-null columns have `None` or 0 correlation.
    - No NaN/Inf values exist in the final JSON-ready matrices.
