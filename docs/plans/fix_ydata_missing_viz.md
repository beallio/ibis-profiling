# Plan: Fix Missing Values Visualization in ydata-theme

The goal is to fix two visual issues in the `ydata-like.html` template:
1. **Missing count labels** in the missing values histogram are currently hidden (only show on hover). They should be always visible.
2. **Nullity matrix sizing** and label layout need improvement, especially for datasets with many columns.

## Proposed Changes

### 1. Missing Values Histogram Count Labels
- **File**: `src/ibis_profiling/templates/ydata-like.html`
- **Location**: Around line 677.
- **Action**: Remove `opacity-0 group-hover:opacity-100 transition-opacity` from the count label `div`. 
- **Action**: Ensure the label is positioned correctly above the bar.

### 2. Nullity Matrix Sizing and Labels
- **File**: `src/ibis_profiling/templates/ydata-like.html`
- **Location**: `NullityMatrix` component (around line 239).
- **Action**: 
    - Set the container `min-w` to `Math.max(800, numCols * 25) + "px"` to ensure columns are wide enough for labels and visibility.
    - Change column label rotation from `-rotate-45` to `-rotate-90` (vertical) or `-rotate-[70deg]` for better fit when many columns are present.
    - Adjust the label `div` height and the `-rotate` origin to ensure they line up with the center of the columns.
    - Make the `sparkline` on the right slightly wider if needed for readability.
    - Ensure the histogram count labels are always visible and formatted clearly.

## Verification Plan

### Automated Tests
- No new automated tests needed as these are purely visual template changes.
- Existing tests (e.g., `test_ydata_theme.py`) should still pass to ensure no regressions in data binding.

### Manual Verification
- Run `scripts/generate_varied_matrices.py` to generate a report with many columns and varied missingness.
- Inspect the generated HTML:
    - Verify that count labels on the histogram are always visible.
    - Verify that the nullity matrix labels are readable and the matrix itself is well-proportioned even with many columns.
- Use `scripts/take_screenshots.py` to capture and verify the results visually.
