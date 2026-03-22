# Plan: Update Documentation and Screenshots

## Objective
Update the project's documentation (`README.md`) and regenerate all screenshots to reflect the latest UI changes and features.

## Key Files & Context
- `README.md`: Main project documentation.
- `scripts/take_screenshots.py`: Utility for generating screenshots using Playwright.
- `scripts/generate_sample_reports.py`: Script to generate the HTML reports used as screenshot sources.
- `src/ibis_profiling/assets/img/`: Directory where screenshots and logos are stored.

## Implementation Steps

### Phase 1: Preparation
1. Ensure `playwright` and its dependencies are installed in the environment.
2. Verify that `scripts/generate_sample_reports.py` is up-to-date with current `ProfileReport` API.

### Phase 2: Generate Fresh Reports
1. Run `scripts/generate_sample_reports.py` to produce `examples/html/full_report.html` and `examples/html/minimal_report.html`.
2. These reports will serve as the "ground truth" for the screenshots.

### Phase 3: Update Screenshots
1. Use `scripts/take_screenshots.py` to capture new images:
   - `report_preview.png` (Full page)
   - `report_overview.png` (Overview section)
   - `report_variables.png` (Variables section)
   - `report_missing.png` (Missing values analysis)
2. Ensure the screenshots are saved directly to `src/ibis_profiling/assets/img/`.

### Phase 4: Update Documentation
1. Review `README.md` for any outdated information:
   - Check if the "Preview" section correctly links to the new images.
   - Verify feature lists (e.g., ensure "Excel Support" and "Adjustable Themes" are accurately described).
   - Check the "Performance Benchmarks" table for any needed updates based on recent optimizations.
   - Ensure the "Usage" examples reflect the current CLI and API.
2. Increment the `cacheBuster` in the PyPI badge URL to force a refresh on GitHub/PyPI.

## Verification & Testing
1. Visually inspect the generated screenshots to ensure they are high-quality and accurately represent the current UI.
2. Review `README.md` locally to ensure all links and images render correctly.
3. Run `ruff check README.md` (if applicable) or verify markdown formatting.
