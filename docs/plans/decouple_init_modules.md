# Plan: Decouple Profiler and ProfileReport from `__init__.py`

## Problem Definition
The `src/ibis_profiling/__init__.py` file is oversized (~900 lines), containing core orchestration logic (`Profiler` class) and compatibility wrappers (`ProfileReport`). This makes the entry point heavy and violates separation of concerns.

## Architecture Overview
1.  **Profiler Migration**: Move the `Profiler` class and its helper methods to a new module `src/ibis_profiling/profiler.py`.
2.  **Wrapper Migration**: Move the `ProfileReport` compatibility wrapper to `src/ibis_profiling/wrapper.py`.
3.  **Clean Export**: Update `src/ibis_profiling/__init__.py` to act as a clean entry point that exports the public API (`ProfileReport`, `profile`, `registry`, etc.).
4.  **Circular Dependency Guard**: Ensure that imports between `profiler.py`, `wrapper.py`, and `report.py` do not create circular references.

## Core Data Structures
No changes to data structures. This is a structural refactor.

## Public Interfaces
- `ibis_profiling.ProfileReport`: Remains the primary user-facing class.
- `ibis_profiling.profile`: Stays available as a functional entry point.

## Phased Approach

### Phase 1: Infrastructure (Module Creation)
- [ ] Create `src/ibis_profiling/profiler.py` with necessary imports.
- [ ] Create `src/ibis_profiling/wrapper.py` with necessary imports.
- [ ] Initialize `feat/decouple-init-modules` branch.

### Phase 2: Logic Migration (Profiler)
- [ ] Move `Profiler` class from `__init__.py` to `profiler.py`.
- [ ] Move `profile()` and `profile_excel()` functions to `profiler.py`.
- [ ] Update imports in `profiler.py` to match moved dependencies.

### Phase 3: Wrapper Migration (ProfileReport)
- [ ] Move `ProfileReport` compatibility class to `wrapper.py`.
- [ ] Update `wrapper.py` to import `profile` and `ProfileReport` (internal).

### Phase 4: Integration & Cleanup
- [ ] Refactor `src/ibis_profiling/__init__.py` to import and re-export the public API.
- [ ] Verify `__all__` is correct.

### Phase 5: Verification
- [ ] Run `tests/test_profiler.py` and `tests/test_cli.py`.
- [ ] Run full test suite to ensure no regressions.
- [ ] Verify `from ibis_profiling import ProfileReport` works in a separate script.

## Git Strategy
- Branch: `feat/decouple-init-modules`
- Commits:
    - `feat: create profiler and wrapper modules`
    - `refactor: move Profiler class to profiler.py`
    - `refactor: move ProfileReport wrapper to wrapper.py`
    - `refactor: clean up __init__.py exports`
