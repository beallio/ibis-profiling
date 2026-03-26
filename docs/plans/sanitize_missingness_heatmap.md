# Plan: Sanitize Missingness Heatmap for Non-Finite Values

## Problem Definition
The missingness heatmap calculation only handles `None` values, allowing `NaN` or `Inf` (resulting from correlation math on masks) to leak into the report. This can break JSON consumers and provide incorrect visual feedback.

## Architecture Overview
We will modify `MissingEngine.compute` in `src/ibis_profiling/report/model/missing.py` to:
1.  Use `math.isfinite` to validate each correlation value.
2.  Default non-finite values to `0.0`.
3.  Collect and report warnings when non-finite correlations are encountered.

## Phased Approach

### Phase 1: Implementation
- [x] Modify `src/ibis_profiling/report/model/missing.py`:
    - Import `math`.
    - Update the `final_matrix` population loop to check for finite values.
    - Track pairs that yield non-finite results.
    - Add warnings to the final result if any non-finite values were found.

### Phase 2: Verification (TDD)
- [x] Create `tests/test_missing_heatmap_sanitization.py`:
    - Test with columns that have 0% and 100% missing values (constant masks -> zero variance -> NaN correlation).
    - Assert that the resulting matrix contains only finite numbers (0.0).
    - Assert that a warning is present in the report.
- [x] Run full test suite.

### Phase 3: Documentation
- [x] Update session log.

## Git Strategy
- Branch: `fix/missing-heatmap-sanitization`
- Commits:
    - Sanitize missingness heatmap for NaN/Inf and add warnings.

## Testing Strategy
- The primary verification was `tests/test_missing_heatmap_sanitization.py`.
- Ensure no regressions in `tests/test_missing.py`.
