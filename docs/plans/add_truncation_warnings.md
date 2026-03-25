# Plan: fix: Add missing truncation warnings for correlations and missing data

## Objective
The profiler currently limits the number of columns processed for correlations and missing data visualizations to maintain performance and report size. While the underlying model tracks whether these sections are truncated, the HTML templates (both `default` and `ydata-like`) only display truncation warnings for the `interactions` section. This task will add similar warnings to the `correlations` and `missing` data sections.

## Key Files & Context
- `src/ibis_profiling/templates/default.src.html`: Source for the default React-based theme.
- `src/ibis_profiling/templates/ydata-like.src.html`: Source for the ydata-like React-based theme.
- `src/ibis_profiling/report/model/correlations.py`: Model providing `truncated` flag for correlations.
- `src/ibis_profiling/report/model/missing.py`: Model providing `truncated` flag for missing matrix and heatmap.

## Implementation Steps

### Phase 1: Research & Verification
1.  **Identify truncation flags in the model**:
    - Correlations: `reportData.correlations[type].truncated`
    - Missing Matrix: `reportData.missing.matrix.matrix.truncated`
    - Missing Heatmap: `reportData.missing.heatmap.matrix.truncated`
2.  **Verify presence of flags in generated JSON**: Run a script with 150+ columns and inspect the JSON output.

### Phase 2: Update Default Theme (`default.src.html`)
1.  **Add warning to Correlations section**:
    - Locate the `correlations` tab rendering.
    - Add a conditional `AlertTriangle` warning if any correlation matrix is truncated.
2.  **Add warning to Missing Data section**:
    - Locate the `missing` tab rendering.
    - Add warnings for both the Nullity Matrix and the Nullity Correlation Heatmap if they are truncated.

### Phase 3: Update YData Theme (`ydata-like.src.html`)
1.  **Add warning to Correlations section**:
    - Locate the `correlations` section.
    - Add a ydata-style warning message.
2.  **Add warning to Missing Data section**:
    - Locate the `matrix` and `heatmap` subsections in the missing data analysis.
    - Add appropriate warning messages.

### Phase 4: Build & Verification
1.  **Rebuild minified templates**: Run `./run.sh uv run python scripts/build_templates.py`.
2.  **Verify with reproduction script**: Run a test profiling a wide dataset and visually/programmatically check for the warning strings in the HTML.
3.  **Run full test suite**: Ensure no regressions.

## Git Strategy
- **Branch**: `fix/truncation-warnings`
- **Commits**:
    1.  Add truncation warnings to default theme.
    2.  Add truncation warnings to ydata-like theme.
    3.  Rebuild minified templates.
    4.  Finalize documentation and session log.
