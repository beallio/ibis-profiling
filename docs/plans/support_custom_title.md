# Plan: Support Custom Title in ProfileReport

## Objective
Allow users to pass a `title` parameter to `ProfileReport` (and the `profile` function) to customize the report heading, matching the `ydata-profiling` API.

## Key Files
- `src/ibis_profiling/__init__.py`: Update `profile` signature and `ProfileReport` wrapper.
- `src/ibis_profiling/report/report.py`: Update `ProfileReport` model to accept a title.

## Implementation Steps

### 1. Update Report Model
- Modify `src/ibis_profiling/report/report.py`:
    - Update `ProfileReport.__init__` to accept an optional `title` string.
    - Default to `"Ibis Profiling Report"` if not provided.
    - Assign the title to `self.analysis["title"]`.

### 2. Update Profiling Entry Point
- Modify `src/ibis_profiling/__init__.py`:
    - Update `profile(table, minimal=False, title=None)` signature.
    - Pass `title` to the `InternalProfileReport` (renamed import of `ProfileReport`).
    - Update `ProfileReport` compatibility wrapper to extract `title` from `kwargs` and pass it to `profile`.

## Verification & Testing
- Create a test case that initializes `ProfileReport(table, title="Custom Title")`.
- Verify the generated JSON/Dict contains the custom title in the `analysis` section.
- Run existing tests to ensure no regressions.
