# Plan: Display Empty String Metrics in HTML Reports

## Objective
Enhance the HTML reports (both "default" and "ydata-like" themes) to explicitly display the quantity and percentage of empty strings for each variable and for the dataset as a whole.

## Key Files & Context
- **Report Model**: `src/ibis_profiling/report/report.py` (Finalize dataset-level empty metrics)
- **Source Templates**: 
    - `src/ibis_profiling/templates/default.src.html`
    - `src/ibis_profiling/templates/ydata-like.src.html`
- **Build Script**: `scripts/build_templates.py` (Compiles `.src.html` to `.html`)
- **Tests**: 
    - `tests/test_report_empty_strings.py` (Verify metrics in model)
    - `tests/test_e2e_empty_strings_display.py` (Verify metrics in rendered HTML via Playwright)

## Implementation Steps

### 1. Update Report Model (`src/ibis_profiling/report/report.py`)
- In `_build()`, initialize `n_cells_empty` and `n_vars_with_empty` in `self.table`.
- During variable iteration, accumulate `n_empty` into `n_cells_empty`.
- Increment `n_vars_with_empty` if a variable has `n_empty > 0`.
- Calculate `p_cells_empty` after the loop.

### 2. Update Default Theme (`src/ibis_profiling/templates/default.src.html`)
- **Overview Stat Cards**: Add a new `StatCard` for "Empty Cells" (quantity and percentage).
- **Variable Quick View**: Display `% empty` next to `% null`.
- **Variable Details**: Add an "Empty Strings" row in the "Data Properties" or "Overview" section of the variable detail card.

### 3. Update YData-Like Theme (`src/ibis_profiling/templates/ydata-like.src.html`)
- **Overview Dataset Statistics**: Add "Empty cells", "Empty cells (%)", and "Variables with empty values" rows.
- **Variable Card Overview**: Add an "Empty" row with count and percentage.

### 4. Build Templates
- Run `python scripts/build_templates.py` to compile the source templates into the final minified HTML files.

### 5. Verification & Testing
- **Unit Test**: Create `tests/test_report_empty_strings.py` to ensure `n_cells_empty` and `p_cells_empty` are correctly calculated in the `ProfileReport.table` dictionary.
- **E2E Test**: Create `tests/test_e2e_empty_strings_display.py` using Playwright to:
    - Generate a report from a dataset with known empty strings.
    - Assert that the "Empty Cells" text and the correct percentages appear in both themes.

## Verification
- Run `pytest tests/test_report_empty_strings.py`.
- Run `pytest tests/test_e2e_empty_strings_display.py`.
- Visually inspect `/tmp/ibis-profiling/report_empty_test.html`.
