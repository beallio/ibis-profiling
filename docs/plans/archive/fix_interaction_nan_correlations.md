# Plan: fix: Sanitize non-finite correlations before scoring interactions

## Objective
Address the issue where non-finite correlation values (NaN/Inf) propagate through the interaction column scoring logic, resulting in unstable sorting and suboptimal column selection for pairwise interactions.

## Key Files & Context
- `src/ibis_profiling/report/model/interactions.py`: The `InteractionEngine.compute` method calculates scores for each numeric column based on their average absolute correlation with other columns.
- `tests/test_interactions.py`: Existing tests for interactions.

## Implementation Steps

### Phase 1: Infrastructure & Red Test
1.  **Create a reproduction test**: A dedicated test file `tests/test_interaction_nan_fix.py` to reproduce the issue.
2.  **Verify Red State**: Run the test using `./run.sh uv run pytest tests/test_interaction_nan_fix.py` and confirm it fails to select the most active columns when NaNs are present in the correlation matrix.

### Phase 2: Core Logic Change
1.  **Modify `InteractionEngine.compute`**: In `src/ibis_profiling/report/model/interactions.py`, update the score calculation to treat non-finite values (NaN/Inf) as 0.0 before averaging.

### Phase 3: Verification & Refactor
1.  **Verify Green State**: Run the reproduction test using `./run.sh uv run pytest tests/test_interaction_nan_fix.py` and confirm it now selects the correct (most active) columns.
2.  **Run Full Test Suite**: Ensure no regressions in existing interaction tests and other parts of the codebase by running `./run.sh uv run pytest tests/`.
3.  **Linting & Type Checking**: Run `./run.sh ruff check .` and `./run.sh uv run ty` (if applicable) to ensure code quality.

## Git Strategy
- **Branch**: `fix/interaction-nan-correlations`
- **Commits**:
    1.  Add reproduction test for NaN interaction scoring.
    2.  Sanitize non-finite correlations in InteractionEngine.
    3.  Finalize documentation and session log.

## Verification
- Dedicated test `tests/test_interaction_nan_fix.py`.
- Full test suite `uv run pytest tests/`.
