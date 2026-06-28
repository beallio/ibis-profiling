# Plan: Refactor Parallel Mode to be Backend-Safe

## Problem Definition
The current parallel execution implementation in `ibis_profiling` uses a shared connection across threads with only a small blacklist (`duckdb`, `sqlite`). Many Ibis backends are not thread-safe, and sharing a connection can lead to data races or crashes.

## Architecture Overview
- `Profiler._check_parallel_safety`: Currently checks against a blacklist.
- `Profiler.run`: Initializes `ThreadPoolExecutor` and then checks for safety, potentially shutting it down immediately.

## Proposed Changes
1.  **Infrastructure:**
    - Define a strict `ALLOWLIST_BACKENDS` in `src/ibis_profiling/__init__.py`.
    - Initial allowlist: `set()` (Empty). Most Ibis backends are NOT thread-safe on a single shared connection. Disabling this mode for all backends ensures stability.
2.  **Logic:**
    - Refactor `_check_parallel_safety` to use the allowlist.
    - If a backend is NOT in the allowlist, return its name.
    - If backend name cannot be determined, assume it's UNSAFE (be conservative).
    - In `Profiler.run()`, move the `_check_parallel_safety()` call BEFORE `ThreadPoolExecutor` initialization.
    - Ensure the warning message is correctly added to `report.analysis["warnings"]`.
3.  **Verification:**
    - Create a dedicated test file `tests/test_parallel_safety_refactor.py`.
    - Mock various Ibis backend connections to verify the allowlist logic.
    - Verify that `duckdb` (not in allowlist) forces sequential execution and emits a warning.
    - Verify that `pandas` (in allowlist) allows parallel execution.

## Dependency Requirements
- None

## Testing Strategy
- **Unit Test:** `tests/test_parallel_safety_refactor.py` will use mocking to simulate different backends.
- **Regression Test:** Run full suite with `uv run pytest tests/`.

## Git Strategy
- Branch: `fix/parallel-safety`
- Commit frequency: After each logical change (Logic, Tests, Docs).

## Task List
- [ ] Task 1: Create feature branch `fix/parallel-safety`.
- [ ] Task 2: Implement reproduction test case.
- [ ] Task 3: Refactor `_check_parallel_safety` and `Profiler.run`.
- [ ] Task 4: Verify with tests and full suite.
- [ ] Task 5: Update documentation (README.md if needed).
- [ ] Task 6: Session log.
