# Plan: Idempotent and Side-Effect Safe Report Finalization

## Problem Definition
`ProfileReport.finalize()` contains logic that recalculates derived metrics and resets table-wide counters. Currently, it is called by both `Profiler.run()` and `ProfileReport.to_dict()`, leading to redundant work and potential side effects if called multiple times.

## Architecture Overview
1.  **Guarded Finalization**: Add a `self._finalized` boolean flag to `ProfileReport`.
2.  **Single-Shot Execution**: Update `finalize()` to return immediately if `self._finalized` is True. Set it to True upon successful completion.
3.  **Thread Safety**: While the profiler is currently single-threaded for finalization, guarding the flag ensures consistency across all serialization paths.

## Core Data Structures
- `ProfileReport._finalized`: Boolean flag.

## Public Interfaces
No changes to public interfaces.

## Phased Approach

### Phase 1: Implementation
- [ ] Initialize `self._finalized = False` in `ProfileReport.__init__`.
- [ ] Update `ProfileReport.finalize()` to check and set the flag.

### Phase 2: Verification
- [ ] Create `tests/test_idempotency.py`.
- [ ] Verify that multiple calls to `to_dict()` do not result in repeated calls to the underlying engine (e.g., `AlertEngine`).
- [ ] Verify that report data remains stable across multiple `to_json()` or `to_html()` calls.
- [ ] Run full test suite.

## Git Strategy
- Branch: `fix/idempotent-finalize`
- Commits:
    - `refactor: add _finalized guard to ProfileReport.finalize`
