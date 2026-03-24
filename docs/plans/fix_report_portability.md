# Plan: Fix Report Portability and CORS Errors

## Problem Definition
Opening generated HTML reports locally (`file://` protocol) triggers several errors in modern browsers (Edge, Chrome, Safari):
1. **CORS Policy Violations:** `esm.sh` and browsers block ES module imports from `origin 'null'`.
2. **Tracking Prevention:** JIT scripts like Babel and Tailwind (development version) are often flagged or blocked from accessing storage.
3. **Broken Renders:** When dependencies fail to load, the entire React application fails to mount.

## Proposed Solution
Switch from ES modules (which require an origin) to **UMD (Universal Module Definition)** builds. UMD builds are standard JavaScript files that define global variables, making them immune to the `origin 'null'` CORS restriction when loaded via standard `<script>` tags.

## Key Files & Context
- `src/ibis_profiling/templates/default.html`
- `src/ibis_profiling/templates/ydata-like.html`

## Implementation Plan

### Phase 1: Update `default.html`
- [ ] Remove `<script type="importmap">`.
- [ ] Add `<script src="...">` for React, ReactDOM, and Lucide-React (UMD versions).
- [ ] Update JSX block:
    - Remove `type="module"` / `data-type="module"`.
    - Replace `import { ... } from 'react'` with `const { ... } = React`.
    - Replace `import { ... } from 'lucide-react'` with `const { ... } = lucideReact`.
    - Update `createRoot` to `ReactDOM.createRoot`.

### Phase 2: Update `ydata-like.html`
- [ ] Apply identical transformations to the `ydata-like` template.

### Phase 3: Infrastructure Improvements (Optional/Future)
- [ ] Consider embedding minified scripts for a "Zero-Internet" mode. (Out of scope for this immediate fix).

## Verification Plan
1. **Manual Check:**
    - Generate a report: `./run.sh uv run python scripts/generate_sample_reports.py`.
    - Open `src/ibis_profiling/examples/html/default_full.html` (or similar) directly in a browser using `file://`.
    - Check console for `net::ERR_FAILED` or `CORS` errors.
2. **Automated Check:**
    - Run existing frontend tests: `./run.sh uv run pytest tests/test_e2e_frontend.py`.

## Git Strategy
- Branch: `fix/report-portability`
- Commits:
    - `Fix: Update default template to use UMD builds for portability`
    - `Fix: Update ydata-like template to use UMD builds for portability`
