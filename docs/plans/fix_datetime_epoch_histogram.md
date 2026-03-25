# Plan: Fix DateTime histogram conversion for numeric epochs

## Problem Definition
1.  Truthiness checks skip valid min/max = 0 for datetime epochs, causing histograms to be silently dropped.
2.  `to_timestamp` helper should handle numeric epoch values (int/float).

## Architecture Overview
The fix involves:
- Updating `to_timestamp` helper in `_run_advanced_pass` to handle `int` and `float` inputs.
- Changing truthiness checks for `v_min_raw` and `v_max_raw` to explicit `is not None` checks.

## Phased Approach

### Phase 1: Infrastructure & Reproduction
- [x] Create reproduction script `tests/reproduce_datetime_epoch_0.py`.
- [x] Verify bug: DateTime histogram is dropped for epoch 0.
- [x] Create a new feature branch `fix/datetime-epoch-histogram`.

### Phase 2: Implementation
- [x] Modify `src/ibis_profiling/__init__.py`:
    - Update `to_timestamp` to handle `int` and `float`.
    - Change truthiness checks to explicit `None` checks.

### Phase 3: Verification
- [x] Run reproduction test and verify histogram is created.
- [x] Run full test suite.
- [x] Update session log.

## Git Strategy
- Branch: `fix/datetime-epoch-histogram`
- Commits:
    - Fix datetime epoch conversion and truthiness checks for histograms.

## Testing Strategy
- The reproduction test `tests/reproduce_datetime_epoch_0.py` was the primary verification.
- Ensure that `v_min` and `v_max` are correctly calculated for epoch 0.
