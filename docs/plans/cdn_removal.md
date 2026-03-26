# Plan: Eliminate Remote CDN Dependencies in Report Templates

## Problem Definition
The generated HTML reports currently load assets from public CDNs (`cdn.tailwindcss.com`, `unpkg.com`). 
This introduces:
1. Supply-chain risks.
2. Data-exfiltration risks (if report contains sensitive data).
3. Dependency on an internet connection for viewing reports.

## Architecture Overview
- `ProfileReport.to_html()` and `ProfileReport.to_file()` will be updated to support an `offline` parameter (default: `True`).
- Templates (`default.html`, `ydata-like.html`) will use placeholders for JS dependencies.
- Local copies of JS dependencies will be stored in `src/ibis_profiling/vendor/js/`.

## Core Data Structures
- `OFFLINE_ASSETS`: A mapping of placeholders to local file content.
- `ONLINE_ASSETS`: A mapping of placeholders to `<script>` tags with SRI hashes.

## Proposed Changes

### Phased Approach

#### Phase 1: Infrastructure (Asset Management)
- Store `react`, `react-dom`, `lucide-react`, and `tailwindcss` in `src/ibis_profiling/vendor/js/`.
- Ensure these are packaged by updating `MANIFEST.in` or equivalent if necessary (checked `pyproject.toml`, it uses `hatch` or similar which usually includes all tracked files).

#### Phase 2: Logic (Report Generation)
- Update `ProfileReport.to_html()` signature: `to_html(self, theme="default", minify=True, offline=True)`.
- Update `ProfileReport.to_file()` signature to pass through `offline`.
- Implement logic to load local assets and inject them into the HTML.
- Implement restrictive Content Security Policy (CSP) when `offline=True`.
- Implement SRI hashes and CSP when `offline=False`.

#### Phase 3: UI (Templates)
- Refactor `src/ibis_profiling/templates/default.html` and `src/ibis_profiling/templates/ydata-like.html` to use placeholders for JS/CSS assets.

#### Phase 4: Verification
- Create `tests/test_offline_rendering.py`.
- Assert that no `http://` or `https://` strings exist in the generated HTML when `offline=True` (excluding `REPORT_DATA` and metadata).
- Assert that the report still functions (smoke test using `playwright` if possible, otherwise just HTML inspection).

## Dependency Requirements
- `curl` (used during research to fetch assets).
- No new third-party Python libraries.

## Testing Strategy
- **TDD:** Write a test that fails when remote URLs are present in the output.
- **Offline rendering check:** Verify the output HTML contains the full source of the libraries.

## Git Strategy
- Branch: `fix/cdn-dependencies`
- Commit after each phase.

## Performance Benchmarking
- **Baseline (dev):** 0.1423s (avg of 10 iterations)
- **Fixed (working branch, offline=True):** 0.1416s (avg of 10 iterations)
- **Impact:** Negligible. The overhead of reading local files and string replacement is comparable to the original template reading.

## Task List
- [x] Task 1: Download JS assets to `src/ibis_profiling/vendor/js/`.
- [x] Task 2: Refactor templates to use placeholders.
- [x] Task 3: Implement `offline` logic in `ProfileReport.to_html()`.
- [x] Task 4: Add SRI hashes and CSP logic.
- [x] Task 5: Add `offline` parameter to CLI.
- [x] Task 6: Verify with new tests.
- [x] Task 7: Update documentation.
