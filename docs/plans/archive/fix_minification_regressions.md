# Plan: Fix Minification Regressions and CSS Parsing Errors

## Problem Definition
1. **Dangerous Minification:** `report.py` uses a naive regex to remove `/* ... */` comments. This regex can span multiple lines and tags, potentially deleting critical application code, especially in pre-compiled templates that contain many `/*#__PURE__*/` markers.
2. **JSON.parse Errors:** If critical JS initialization code is accidentally deleted by the minifier, variables like `REPORT_DATA` may become `undefined`, leading to `JSON.parse` errors.
3. **CSS Warnings:** Modern browsers (Edge/Chrome) report "bad selector" and "parsing value" errors for certain Tailwind-generated or custom styles.

## Proposed Solution
1. **Remove Naive Minifier:** Delete the `re.sub(r"/\*.*?\*/", ...)` and `re.sub(r"<!--.*?-->", ...)` logic from `src/ibis_profiling/report/report.py`. Pre-compiled templates are already minified/optimized where it matters.
2. **Clean Source CSS:** Update `default.src.html` and `ydata-like.src.html` to remove problematic comments or legacy CSS properties that trigger browser warnings.
3. **Robust Decoding:** Add a `try-catch` around the report data decoding logic in the templates to provide better error messaging if data loading fails.

## Key Files & Context
- `src/ibis_profiling/report/report.py`
- `src/ibis_profiling/templates/*.src.html`

## Implementation Plan

### Phase 1: Fix Report Logic
- [ ] Remove naive HTML and JS comment removal from `ProfileReport._build` in `report.py`.
- [ ] Keep the whitespace stripping as it's relatively safe.

### Phase 2: Update Source Templates
- [ ] Remove inline comments from `<style>` tags in `.src.html` files.
- [ ] Add `try-catch` around `JSON.parse(new TextDecoder().decode(bytes))` with a clear console error if it fails.

### Phase 3: Regenerate Templates
- [ ] Run `./run.sh uv run python scripts/build_templates.py` to update the production `.html` templates.

### Phase 4: Verification
- [ ] Run full test suite.
- [ ] Manually verify that `test_export.html` (generated report) no longer has the reported errors.

## Git Strategy
- Branch: `fix/minification-and-css-cleanup`
- Commits:
    - `Fix: Remove dangerous naive minification logic in report.py`
    - `Fix: Cleanup template CSS and add robust data decoding`
