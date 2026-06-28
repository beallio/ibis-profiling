# Plan: Validate Correlation Sampling Parameters

## Problem Definition
Sampling parameters (`sample_size`, `sampling_threshold`) are user-controlled but currently lack validation. Zero or negative values can lead to invalid sample fractions or division by zero errors.

## Architecture Overview
The solution involves adding input validation in the `Profiler` constructor and adding defensive guards in the `CorrelationEngine`.

- **Profiler**: Validate parameters during initialization. If invalid, reset to defaults and record a warning in the report analysis.
- **CorrelationEngine**: Add a division-by-zero guard for `row_count` and ensuring `sampling_threshold` is used safely.

## Core Data Structures
- `report.analysis["warnings"]`: Will contain validation warnings.

## Public Interfaces
- No changes to public interfaces (validation is internal to constructor).

## Dependency Requirements
- No new dependencies.

## Testing Strategy
- **Functional**: `tests/test_sampling_validation.py` will verify that:
    - Zero or negative `sample_size` or `sampling_threshold` are handled gracefully.
    - A warning is emitted when parameters are adjusted.
    - No crash occurs when the table is empty (`row_count=0`).

## Phased Approach

### Phase 1: Infrastructure & API
- [ ] Create feature branch `fix/validate-sampling-parameters`.
- [ ] Create `tests/test_sampling_validation.py`.

### Phase 2: Core Logic (Validation)
- [ ] Implement validation in `Profiler.__init__` in `src/ibis_profiling/__init__.py`.
- [ ] Implement defensive guards in `CorrelationEngine.compute_all` in `src/ibis_profiling/report/model/correlations.py`.
- [ ] Verify `tests/test_sampling_validation.py` passes.

### Phase 3: Verification & Cleanup
- [ ] Run full test suite.
- [ ] Run apples-to-apples benchmark (regression check).
- [ ] Execute PE review.
- [ ] Submit PR.

## Git Strategy
- Branch: `fix/validate-sampling-parameters`
- Commit after each functional step.
