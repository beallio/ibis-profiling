# Visual Regression Baseline Implementation

- Added deterministic Playwright screenshot coverage for the default and ydata-like themes.
- Captured full-page, variables, correlations, interactions, and missing-data baselines.
- Verified the committed baselines pass twice consecutively without update mode.
- Drift sanity-check: changed the default histogram fill from blue to red, rebuilt the templates,
  and confirmed the visual test failed through the pixel-diff assertion at a 0.031082 ratio. The
  test wrote actual and red-diff artifacts under `/tmp/ibis-profiling/visual_artifacts/`.
- Restored the blue histogram fill, rebuilt the templates, and confirmed the frontend sources and
  generated templates had no remaining diff.
