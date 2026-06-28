# Plan: Fix Template Issues

## Problem Definition
Several issues have been identified in the HTML templates (default and ydata-like):
1.  **Default Theme:** Misplaced "Nullity Matrix" truncation warning (above header).
2.  **Default Theme:** Missing/Inaccessible "Nullity Correlation Heatmap" truncation warning.
3.  **Ydata Theme:** Misplaced "Nullity Matrix" truncation warning (above header).
4.  **Ydata Theme:** Missing/Inaccessible "Nullity Correlation Heatmap" truncation warning.
5.  **Ydata Theme:** Incorrect `_metadata` button in Correlations section.

## Architecture Overview
The fixes involve modifying `src/ibis_profiling/templates/default.src.html` and `src/ibis_profiling/templates/ydata-like.src.html`. These source templates are then processed into the final `.html` files.

## Phased Approach

### Phase 1: Infrastructure & Reproduction
- [x] Create reproduction script `tests/reproduce_truncation_warning.py`.
- [x] Verify truncation metadata is correctly populated in `report_data`.
- [x] Create a new feature branch `fix/template-issues`.

### Phase 2: Fix Default Theme
- [x] Move "Nullity Matrix" warning inside the `NullityMatrix` component or after its header.
- [x] Investigate and fix the "Nullity Correlation Heatmap" warning (ensure correct path and visibility).
- [x] Ensure `AlertTriangle` and other icons are correctly used.

### Phase 3: Fix Ydata Theme
- [x] Filter out `_metadata` from the Correlations section tab buttons.
- [x] Move "Nullity Matrix" warning inside the `NullityMatrix` component or after its header.
- [x] Fix the data path for `CorrelationMatrixComponent` in the Null Heatmap section (pass the dict, not just the matrix list).
- [x] Ensure correct path and visibility for the Heatmap truncation warning.

### Phase 4: Verification & Documentation
- [x] Run reproduction script and verify generated HTML (visual check or grep on decoded content).
- [x] Run full test suite.
- [x] Update session log.

## Git Strategy
- Branch: `fix/template-issues`
- Commits:
  - Fix default theme nullity matrix warning and heatmap warning.
  - Fix ydata theme correlations metadata button.
  - Fix ydata theme nullity matrix warning and heatmap data path/warning.

## Testing Strategy
- Use `tests/reproduce_truncation_warning.py` to generate reports with many columns.
- Manually inspect the generated HTML or use a script to decode the Base64 and check for the existence/position of warnings.
- Automated tests in `tests/test_report.py` (if applicable) to ensure no regressions.
