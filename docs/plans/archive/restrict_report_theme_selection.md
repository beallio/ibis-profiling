# Plan: Restrict Report Theme Selection to a Safe Allowlist

## Objective
Address a security vulnerability where user-controlled `theme` is used in a filesystem path without validation. This prevents path traversal and arbitrary file reads.

## Key Files & Context
- `src/ibis_profiling/report/report.py`: Contains `ProfileReport.to_html` where the vulnerability exists.
- `src/ibis_profiling/templates/`: Directory containing allowed HTML templates (`default.html`, `ydata-like.html`).

## Proposed Solution
1. Define an internal allowlist of supported themes: `{"default", "ydata-like"}`.
2. In `to_html(theme=...)`, validate the `theme` argument against this allowlist.
3. If the theme is invalid:
    - Default back to `"default"`.
    - Record a warning in `self.analysis["warnings"]` to inform the user of the invalid selection.
4. Implement an additional safety check using `os.path.realpath` to ensure the resolved template path is strictly within the `templates` directory.
5. Add a dedicated security test case to verify that path traversal attempts are blocked and fall back to the default theme.

## Implementation Steps

### Phase 1: Security Testing (Red)
1. [x] **Task**: Create `tests/test_theme_security.py`.
    - **Scope**: Define a test that passes `theme="../LICENSE"` (or any sensitive file) to `to_html`.
    - **Validation**: Assert that the call succeeds but uses the default template, and that a warning is recorded in the report's analysis data. Run with `./run.sh uv run pytest tests/test_theme_security.py`.
    - **Commit**: `Add failing security test for theme path traversal`

### Phase 2: Core Logic Fix (Green)
2. [x] **Task**: Update `src/ibis_profiling/report/report.py`.
    - **Scope**:
        - Define `ALLOWED_THEMES = {"default", "ydata-like"}` inside `to_html` (or as a class constant).
        - Add validation logic at the start of `to_html`.
        - Add `self.analysis.setdefault("warnings", [])` and append a warning if `theme` is invalid.
        - Use `os.path.realpath` to verify the final `template_path` prefix matches the `templates` directory.
    - **Validation**: Run `./run.sh uv run pytest tests/test_theme_security.py` and ensure it passes.
    - **Commit**: `Restrict report theme selection to safe allowlist`

### Phase 3: Regression & Cleanup
3. [x] **Task**: Run full test suite.
    - **Scope**: Ensure no existing report generation tests are broken.
    - **Validation**: `./run.sh uv run pytest tests/test_report.py tests/test_profiler.py`
    - **Commit**: `Verify no regressions in report generation`

## Verification & Testing
- **New Test**: `tests/test_theme_security.py` will specifically target the vulnerability.
- **Manual Verification**: Generate a report with an invalid theme and inspect `report.to_dict()["analysis"]["warnings"]`.
- **Existing Tests**: All tests in `tests/` must pass.
- **Mandatory**: All commands MUST be executed via `./run.sh` (e.g., `./run.sh uv run pytest ...`).

## Git Strategy
- **Branch**: `fix/restrict-theme-selection`
- **Commit Frequency**: After each task completion.

