# Plan: Fix Import-time Version Resolution

## Problem Definition
Importing `ibis_profiling` calls `git describe` at import time in `src/ibis_profiling/_version.py`. This adds latency (~50ms-200ms) and can fail in environments without Git or in sandboxed environments.

## Architecture Overview
We will move to lazy version resolution using Python 3.7+ module-level `__getattr__` in `src/ibis_profiling/__init__.py`. This ensures that Git (the slow fallback) is ONLY called if `__version__` is explicitly accessed and cannot be found in the installed package metadata.

## Core Data Structures
-   No changes to data structures.
-   `ibis_profiling.__version__` remains a string.

## Public Interfaces
-   `ibis_profiling.__version__` is preserved but lazy.
-   `ibis_profiling._version.get_version()` remains available for manual calls.

## Dependency Requirements
-   Python >= 3.7 (module-level `__getattr__`)
-   `importlib.metadata` (Python 3.8+) or `importlib_metadata` fallback.

## Phased Implementation Plan

### Phase 1: Research & TDD (RED)
-   **Task 1.1: Create a test verifying Git call at import time**
    -   **Scope**: Create `tests/test_version_latency.py` using `unittest.mock.patch` on `subprocess.check_output` during a fresh import.
    -   **Inputs**: `tests/`
    -   **Outputs**: `tests/test_version_latency.py`
    -   **Validation**: `./run.sh uv run pytest tests/test_version_latency.py` (should fail or report 1 call to git).

### Phase 2: Implementation (GREEN)
-   **Task 2.1: Clean up `_version.py`**
    -   **Scope**: Remove `__version__ = get_version()` from `src/ibis_profiling/_version.py`. Ensure `get_version()` is robust.
    -   **Inputs**: `src/ibis_profiling/_version.py`
    -   **Outputs**: Modified `_version.py` containing only the function.
    -   **Validation**: Test `get_version()` still works.

-   **Task 2.2: Implement Lazy Load in `__init__.py`**
    -   **Scope**: Remove `from ._version import __version__` from `src/ibis_profiling/__init__.py` and implement module-level `__getattr__`.
    -   **Inputs**: `src/ibis_profiling/__init__.py`
    -   **Outputs**: Updated `__init__.py`.
    -   **Validation**: Verify `ibis_profiling.__version__` works and Task 1.1 passes (0 Git calls at import).

### Phase 3: Downstream & Verification
-   **Task 3.1: Verify Report and CLI**
    -   **Scope**: Ensure `report.py` and CLI still correctly see the version.
    -   **Inputs**: Project root.
    -   **Outputs**: Verified functionality.
    -   **Validation**: Run existing `tests/test__version.py`.

## Git Strategy
-   **Branch**: `fix/lazy-versioning`
-   **Commit Frequency**: After each task (1.1, 2.1, 2.2, 3.1).
-   **Commit Messages**: Imperative (e.g., "Implement lazy __version__ resolution").

## Performance Impact
Import latency of `ibis_profiling` should decrease by 50ms-200ms as it will no longer fork a subprocess for `git describe`.

## Tool Strategy
- **Use ./run.sh**: Use ./run.sh before executing any command to ensure the correct environment variables are loaded.
- **Temp file storage**: Ensure are temporary, and ephermal files are stored in /tmp/ibis-profiling
