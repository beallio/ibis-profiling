# Plan: Clamp Correlation Sampling Fraction

## Problem Definition
In `CorrelationEngine.compute_all`, if `sample_size` exceeds `row_count` while `row_count > sampling_threshold`, the calculation `table.sample(sample_size / row_count)` results in a sampling fraction greater than 1.0. This causes some Ibis backends to throw an error.

## Architecture Overview
The fix involves ensuring the sampling fraction is always clamped to a maximum of 1.0. If the fraction is 1.0 or greater, sampling should be skipped entirely as the "sample" would be the entire table (or more).

## Core Data Structures
No changes to data structures.

## Public Interfaces
No changes to public interfaces.

## Dependency Requirements
No new dependencies.

## Git Strategy
- Branch: `fix/clamp-correlation-sampling`
- Commit frequency: Incremental commits after each functional change.

## Testing Strategy
- Create `tests/test_correlation_sampling_clamp.py`.
- Verify behavior when `sample_size > row_count` and `row_count > sampling_threshold`.
- Verify that no error is thrown and the result is correct.

## Phased Approach

### Phase 1: Infrastructure
- [ ] Create feature branch `fix/clamp-correlation-sampling`.
- [ ] Create reproduction test `tests/test_correlation_sampling_clamp.py` (RED).

### Phase 2: Core Logic
- [ ] Implement clamping logic in `src/ibis_profiling/report/model/correlations.py` (GREEN).
- [ ] Verify test passes.

### Phase 3: Verification & Cleanup
- [ ] Run full test suite to ensure no regressions.
- [ ] Execute PE review.
- [ ] Submit PR.
