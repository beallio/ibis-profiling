# Plan: Nest Correlation Metadata

Fix the UI issue where correlation truncation metadata appears as selectable types (buttons) in the report.

## Problem Definition
`CorrelationEngine.compute_all` returns metadata fields (`truncated`, `original_count`, `limit`) at the same level as the correlation types (`pearson`, `spearman`). The UI templates iterate over all keys in the `correlations` object, causing these metadata fields to appear as buttons in the correlations section.

## Architecture Overview
1.  **Model Update:** Nest truncation metadata under a `_metadata` key in the `CorrelationEngine.compute_all` return dictionary.
2.  **Orchestration Update:** Update `Profiler._run_correlations` to read from the new nested structure.
3.  **UI Update:** Update `default.html` and `ydata-like.html` to filter out the `_metadata` key when rendering correlation buttons.
4.  **Test Update:** Update `tests/test_correlations_cap.py` to verify the new structure.

## Phased Approach

### Phase 1: Logic & Model
- [ ] Modify `src/ibis_profiling/report/model/correlations.py`: Nest metadata in `_metadata`.
- [ ] Modify `src/ibis_profiling/__init__.py`: Update `_run_correlations` to access nested metadata.

### Phase 2: UI Templates
- [ ] Modify `src/ibis_profiling/templates/default.html`: Filter `_metadata` from correlation keys.
- [ ] Modify `src/ibis_profiling/templates/ydata-like.html`: Filter `_metadata` from correlation keys.

### Phase 3: Verification
- [ ] Update `tests/test_correlations_cap.py`.
- [ ] Run full test suite.

## Git Strategy
- **Branch:** `fix/correlation-metadata-nesting`
- **Commits:**
  - Nest correlation metadata in model and update profiler.
  - Filter metadata key in HTML templates.
  - Update correlation truncation tests.
