# Fix `from_excel` Kwargs Misrouting

## Objective
Address code review finding: `ProfileReport.from_excel` misroutes profiling kwargs to `pl.read_excel`, causing errors or ignored settings when parameters like `correlations=False` or `compute_duplicates=False` are passed. We will implement a dynamic kwarg splitting mechanism using `inspect.signature` to accurately separate profiling options from Excel reading options.

## Key Files & Context
- `src/ibis_profiling/report/report.py`: Contains `ProfileReport.from_excel`.
- `tests/test_report.py` (or similar): For asserting correct behavior.
- `docs/benchmarking_protocol.md`: Protocol for performance regression testing.

## Implementation Plan (Phased Approach)

### Phase 1: Preparation & Branching
- **Task 1.1**: Run `./run.sh git checkout -b fix/from-excel-kwargs-misrouting` to create and switch to a new working branch.
- **Task 1.2**: Copy the implementation plan to `docs/plans/fix_from_excel_kwargs.md` to persist it in the repository.
- **Task 1.3**: Ensure that environment variables and output directories correctly point to `/tmp/ibis-profiling` during execution (this will be done using `./run.sh` prefix for all commands).

### Phase 2: Test-Driven Development (Red)
- **Task 2.1**: Identify the appropriate test file (e.g., `tests/test_report.py` or create a new `tests/test_from_excel.py`).
- **Task 2.2**: Write a failing test `test_from_excel_kwargs_routing` that calls `ProfileReport.from_excel` with `correlations=False` and `compute_duplicates=False`. The test should mock or use a tiny Excel file (generated in `/tmp/ibis-profiling`) to verify that polars does not throw a `TypeError`.
- **Task 2.3**: Run `./run.sh uv run pytest` to confirm the test fails (Red state).
- **Task 2.4**: Run `./run.sh git add tests/` and `./run.sh git commit -m "test: add failing test for from_excel kwargs routing"` to commit the failing test. Update the plan document at `docs/plans/fix_from_excel_kwargs.md` and commit it too if any changes are made to the plan.

### Phase 3: Implementation (Green)
- **Task 3.1**: Modify `src/ibis_profiling/report/report.py`.
- **Task 3.2**: In `from_excel`, import the `inspect` module.
- **Task 3.3**: Use `inspect.signature(profile).parameters.keys()` to dynamically extract all valid profiling argument names.
- **Task 3.4**: Replace the hardcoded `profile_keys = ["minimal", "title"]` with the dynamically extracted set of keys.
- **Task 3.5**: Route any `kwargs` present in the signature to `profile_kwargs`, and route the remainder to `read_kwargs`.
- **Task 3.6**: Run `./run.sh uv run pytest` to verify the test passes (Green state).
- **Task 3.7**: Run `./run.sh git add src/` and `./run.sh git commit -m "fix: dynamically route kwargs in from_excel based on profile signature"` to commit the implementation.

### Phase 4: Refactor & Validation
- **Task 4.1**: Check if any other static lists exist in `from_excel` or related functions that should also be dynamic, and refactor if necessary.
- **Task 4.2**: Run `./run.sh uv run ruff check . --fix` and `./run.sh uv run ruff format .` to ensure linting and formatting standards.
- **Task 4.3**: Run the full test suite with `./run.sh uv run pytest` to ensure no regressions.
- **Task 4.4**: If refactoring was performed, run `./run.sh git add src/ tests/` and `./run.sh git commit -m "refactor: clean up and format kwargs routing implementation"`.

### Phase 5: Benchmarking
- **Task 5.1**: Ensure the worktree is clean before benchmarking.
- **Task 5.2**: Run the scalability backtest using `./run.sh uv run scripts/quick_backtest.py` to compare performance against the current main branch (or latest release) according to `docs/benchmarking_protocol.md`.
- **Task 5.3**: Verify that the execution time on the Scalability Test has not increased by > 10%. If it has, provide a technical justification or investigate performance bottlenecks.

### Phase 6: Documentation & Completion
- **Task 6.1**: Ensure `docs/plans/fix_from_excel_kwargs.md` (or similar location based on GEMINI.md protocol) is updated and committed.
- **Task 6.2**: Log the session conversation to `docs/agent_conversations/`.
- **Task 6.3**: Commit the session log with `./run.sh git add docs/` and `./run.sh git commit -m "docs: record agent session for from_excel kwargs fix"`.

## Verification & Constraints
- Ensure all caching (`.pytest_cache`, `.ruff_cache`) and temporary files (e.g., sample excel files for tests) correctly resolve to `/tmp/ibis-profiling`.
- All commands MUST be prefixed with `./run.sh`.
- Commit frequently as detailed in the phased approach.