# Plan: Comprehensive Documentation & Screenshot Update (v2)

## Objective
Review the latest features and changes in the codebase to update the project documentation (`README.md`), generate a fresh set of high-quality screenshots using a realistic dataset, and document new use cases.

## Key Files & Context
- `README.md`: Primary user documentation.
- `src/ibis_profiling/profiler.py`: Source of truth for new parameters and features.
- `src/ibis_profiling/report/model/`: Logic for alerts, correlations, interactions, and missing values.
- `scripts/generate_bench_data.py`: Tool for creating a realistic synthetic dataset.
- `scripts/take_screenshots.py`: Playwright-based screenshot utility.
- `src/ibis_profiling/assets/img/`: Target directory for screenshots.

## Implementation Steps

### Phase 1: Data Preparation
1. **Generate a realistic sample dataset**: Use `scripts/generate_bench_data.py` to create a 100k-row, 20-column Parquet file at `/tmp/ibis-profiling/sample_data.parquet`.
2. **Generate representative reports**: Create two main reports for screenshots:
   - `full_report.html`: Default theme, all features enabled.
   - `ydata_theme.html`: YData-like theme for parity demonstration.
   - These will be stored in `/tmp/ibis-profiling/sample_reports/`.

### Phase 2: Screenshot Generation
1. **Verify Playwright setup**: Ensure `playwright` and `chromium` are available in the environment.
2. **Capture new images**: Use `scripts/take_screenshots.py` against `full_report.html` to update:
   - `report_preview.png` (Full page)
   - `report_overview.png` (Overview section)
   - `report_variables.png` (Variables section)
   - `report_missing.png` (Missing values analysis)
3. **Capture theme comparison** (Optional): Consider adding a screenshot showing the theme selector or the difference between default and ydata themes.

### Phase 3: Documentation Update (`README.md`)
1. **Add "Use Cases" section**:
   - Financial Data Integrity Audit (using `generate_financial_reports.py` logic).
   - High-Volume ML Preprocessing (profiling multi-million row datasets).
   - Automated Pipeline Quality Gates (JSON schema parity).
2. **Update Parameters Table**:
   - Add `use_sketches` (approx_nunique support).
   - Add `n_unique_threshold` and `duplicates_threshold` for clarity on performance knobs.
3. **Highlight New Features**:
   - **Pairwise Interactions**: Explicitly mention the correlation-based pruning strategy.
   - **Alerts Expansion**: Mention the `EMPTY` (empty string) alert for categorical columns.
4. **Update Feature List**: Ensure "Modern SPA Report" and "Adjustable Themes" are prominently featured.
5. **Update Badges & Image URLs**: 
   - Increment `cacheBuster` in the PyPI badge.
   - Append or increment `?cacheBuster=...` to all screenshot URLs in `README.md` to ensure GitHub bypasses its image cache.

### Phase 4: Validation
1. **Broken Link Check**: Ensure all new images and links in `README.md` work correctly.
2. **Formatting**: Ensure table alignment and markdown structure are clean.
3. **Consistency**: Verify that the documented parameters match `Profiler.__init__` exactly.

## Verification & Testing
1. **Visual Inspection**: Manually check the generated screenshots for clarity and correctness.
2. **Local Rendering**: View `README.md` in a markdown renderer to ensure images display properly.
