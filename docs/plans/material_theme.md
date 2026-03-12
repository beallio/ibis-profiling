# Implementation Plan: Material Theme

This plan outlines the development of the Materialize CSS-based theme ("material") for the Ibis Profiling report.

## Objective
Develop `src/ibis_profiling/templates/material.html` as a spec-compliant, modern theme featuring a customizable title, global search, and polymorphic sections.

## Key Files
- `src/ibis_profiling/templates/material.html`
- `tests/test_material_theme.py`

## Implementation Steps
1.  **Template Creation**: Use Materialize CSS and React 18 to build a responsive profiling dashboard.
2.  **Polymorphism**: Ensure sections (Correlations, Missing Values, Sample Data) only render if data exists in the payload.
3.  **Title Support**: Dynamically inject the report title from `REPORT_DATA.analysis.title`.
4.  **Enhanced Navigation**: Implement a fixed sidebar with auto-scrolling and active section highlighting.
5.  **Global Search**: Add a sticky search bar to filter variables in real-time.

## Verification
- Run `tests/test_material_theme.py` to confirm HTML generation and title injection.
- Verify component presence (Overview, Quick View, Alerts, Variables).
