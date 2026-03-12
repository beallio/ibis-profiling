# Plan: Fix Nullity Matrix Transposition and Job Duration

## Objective
1.  Populate "Job Duration" in the report with the actual duration from the JSON payload.
2.  Fix the Nullity Matrix rendering by transposing the column-oriented data into row-oriented data in the SPA template.

## Key Files & Context
- `src/ibis_profiling/__init__.py`: Main entry point where profiling starts and ends.
- `src/ibis_profiling/templates/spa.html`: React-based template for the report.
- `src/ibis_profiling/report/report.py`: Report model.

## Implementation Steps

### 1. Update Profiling Logic (Job Duration)
- In `src/ibis_profiling/__init__.py`:
    - Capture `start_time` at the very beginning.
    - At the very end (before returning), capture `end_time`.
    - Update `report.analysis["date_start"]` and `report.analysis["date_end"]`.
    - Add `report.analysis["duration"]` containing the total duration in milliseconds.

### 2. Update SPA Template (Job Duration)
- In `src/ibis_profiling/templates/spa.html`, find the "Job Duration" display.
- Change it to use `reportData.analysis.duration` directly.
- Add a formatter to display it nicely (e.g., in seconds if it's large, otherwise ms).

### 3. Fix Nullity Matrix (Transposition)
- In `src/ibis_profiling/templates/spa.html`, modify `NullityMatrix` component.
- After parsing the data with `parseMatrixData`, transpose the `values` (matrix) from column-oriented to row-oriented.
- Use a robust transposition helper.

## Verification & Testing
1.  Run a profile and check the "Job Duration" in the sidebar.
2.  Check the "Missing" tab and verify the Nullity Matrix shows 250 rows (vertically) and correctly maps columns.
3.  Ensure the "Data Completeness" sparkline correctly reflects row density.
