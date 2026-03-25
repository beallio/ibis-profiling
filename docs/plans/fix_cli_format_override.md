# Plan: fix: Honor --format override regardless of output extension

## Objective
Ensure that the `--format` CLI flag is strictly honored, even if the output file extension suggests a different format. This prevents the tool from automatically switching formats or appending extensions when the user has explicitly requested a specific output format.

## Implementation Steps

### Phase 1: Infrastructure & Red Test
1.  **Create a reproduction test**: `tests/test_cli_format_override.py` to verify that `--format html` produces HTML even with a `.json` extension, and vice versa.
2.  **Verify Red State**: Confirm the test fails by running `./run.sh uv run pytest tests/test_cli_format_override.py`.

### Phase 2: Logic Change
1.  **Modify `src/ibis_profiling/cli.py`**:
    - Update the output generation logic to directly call `report.to_json()` or `report.to_html()` based on the `output_format` variable.
    - Remove the code that automatically appends `.json` to the output filename.
    - Manually write the generated content to the specified output file.

### Phase 3: Verification & Refactor
1.  **Verify Green State**: Confirm the tests pass.
2.  **Run Full Test Suite**: Ensure no regressions.
3.  **Linting & Formatting**: Run `ruff`.

## Git Strategy
- **Branch**: `fix/cli-format-override`
- **Commits**:
    1.  Add reproduction tests for CLI format override.
    2.  Update CLI to honor --format override strictly.
    3.  Finalize documentation and session log.
