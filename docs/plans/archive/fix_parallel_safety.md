# Plan: Guard Parallel Execution against Unsafe Backends

## Problem Definition
Parallel profiling mode (`parallel=True`) submits multiple concurrent Ibis queries against a single backend connection. Many backends, including DuckDB (the primary backend for this project), are not thread-safe for concurrent query execution on a single connection. This can lead to crashes, deadlocks, or incorrect results.

## Architecture Overview
We will implement a backend-capability guard that checks if the current Ibis backend is explicitly marked as thread-safe for shared connections. If not, the profiler will fall back to sequential execution and emit a warning.

## Phased Approach

### Phase 1: Research & Discovery
- [x] Review `Profiler._run_advanced_pass` and `Profiler._run_complex_pass`.
- [x] Research Ibis/DuckDB thread safety (confirmed unsafe).
- [x] Create reproduction script `tests/repro_parallel_safety.py`.

### Phase 2: Logic & Core Implementation
- [x] Define a list of thread-safe Ibis backends (initially empty or very conservative).
- [x] Implement `Profiler._is_parallel_safe()` helper (implemented as `_check_parallel_safety`).
- [x] Update `Profiler.__init__` to disable `self.executor` if the backend is unsafe, or better, keep the logic in `run()` to allow for more granular control/warnings.
- [x] Add a warning to `report.analysis["warnings"]` when parallel mode is requested but disabled due to safety.

### Phase 3: Verification & TDD
- [x] Create `tests/test_parallel_safety.py` to verify fallback behavior.
- [x] Verify that a warning is added to the report when fallback occurs.
- [x] Run the full test suite.

### Phase 4: Documentation
- [x] Update README if necessary to document parallel mode limitations.
- [x] Update session log.

## Git Strategy
- Branch: `fix/parallel-safety`
- Commits:
  - Add thread safety check and sequential fallback logic.
  - Add parallel safety tests.

## Testing Strategy
- A new test file `tests/test_parallel_safety.py` will:
    - Instantiate `Profiler(t, parallel=True)` on a DuckDB table.
    - Assert that `profiler.parallel` (or an internal flag) reflects the fallback.
    - Assert that the final report contains a warning about parallel execution being disabled.
- Full regression check of all existing tests.
