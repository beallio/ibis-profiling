# Plan: Fix Top Values Count Column Detection

## Problem Definition
The `top_values` count column detection logic is fragile and can mislabel counts when column names include "count".
1. `src/ibis_profiling/planner.py#L70`: Assumes a `count` column can be renamed safely, which fails if the source column is already named `count`.
2. `src/ibis_profiling/report/report.py#L233`: Uses string matching ("count" in key) to identify the count column, which fails if the label column name also contains "count".

## Architecture Overview
We will shift from name-based detection to positional detection for `value_counts()` results. Ibis `value_counts()` returns a table where the first column is the value (label) and the second is the count.

## Core Data Structures
No changes to public data structures. Internal mapping within `ProfileReport.add_metric` will be updated.

## Public Interfaces
No changes to public APIs or CLI parameters.

## Dependency Requirements
- `ibis-framework`
- `pytest` for verification

## Phased Approach

### Phase 1: Core Logic Implementation
- **Task 1.1: Update Planner Logic**
    - **Scope**: Remove `.rename({"count": count_col})` in `src/ibis_profiling/planner.py`.
    - **Inputs**: `src/ibis_profiling/planner.py`
    - **Outputs**: Updated `planner.py` that preserves original backend column names.
    - **Validation**: `./run.sh ruff check src/ibis_profiling/planner.py`
- **Task 1.2: Update Report Processor Logic**
    - **Scope**: Modify `src/ibis_profiling/report/report.py` to use positional indexing for keys in `top_values` metrics.
    - **Inputs**: `src/ibis_profiling/report/report.py`
    - **Outputs**: Updated `report.py` using `keys[1]` for counts and `keys[0]` for labels.
    - **Validation**: `./run.sh ruff check src/ibis_profiling/report/report.py`

### Phase 2: Verification (TDD)
- **Task 2.1: Create Robustness Test**
    - **Scope**: Create `tests/test_count_column_robustness.py` with columns named `count` and `item_count`.
    - **Inputs**: `tests/` directory.
    - **Outputs**: `tests/test_count_column_robustness.py`
    - **Validation**: `./run.sh uv run pytest tests/test_count_column_robustness.py`
- **Task 2.2: Regression Testing**
    - **Scope**: Run all existing tests to ensure no breakage.
    - **Inputs**: Full test suite.
    - **Outputs**: Test passing report.
    - **Validation**: `./run.sh uv run pytest`

### Phase 3: Documentation
- **Task 3.1: Update Session Log**
    - **Scope**: Record the changes in `docs/agent_conversations/`.
    - **Inputs**: Execution results.
    - **Outputs**: New session log JSON.
    - **Validation**: File exists.

## Git Strategy
- **Branch**: `fix/top-values-robustness`
- **Commit Frequency**: After each task (1.1, 1.2, 2.1, 2.2, 3.1).
- **Commit Messages**: Imperative (e.g., "Remove fragile rename in planner", "Use positional count detection in report").
- **Environment**: All commands MUST be prefixed with `./run.sh`.

## Performance Impact
None expected. Positional access is marginally faster than string searching.
