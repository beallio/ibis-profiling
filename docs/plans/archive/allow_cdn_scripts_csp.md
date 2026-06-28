# Plan: Allow CDN Scripts in CSP when Online

## Problem Definition
In online mode (`offline=False`), the report injects script tags with `src` pointing to CDNs (e.g., `cdn.tailwindcss.com`, `unpkg.com`). However, the current Content Security Policy (CSP) only allows `'unsafe-inline'` and `'unsafe-eval'` for scripts, causing browsers to block the external CDN assets.

## Architecture Overview
- Update `ProfileReport.to_html` to dynamically construct `csp_directives`.
- When `offline=False`, append `https://cdn.tailwindcss.com`, `https://unpkg.com`, and `'self'` to the `script-src` directive.
- Maintain the existing strict CSP for `offline=True`.

## Core Data Structures
No changes to data structures.

## Public Interfaces
No changes to public interfaces.

## Dependency Requirements
No new dependencies.

## Git Strategy
- Branch: `fix/allow-cdn-csp`
- Commit frequency: Incremental commits after each functional change.

## Testing Strategy
- Create `tests/test_csp_online.py`.
- Verify that the generated HTML in online mode contains the correct CSP meta tag with CDN origins.
- Verify that the generated HTML in offline mode remains strict.

## Phased Approach

### Phase 1: Infrastructure
- [ ] Create feature branch `fix/allow-cdn-csp`.
- [ ] Create reproduction test `tests/test_csp_online.py` (RED).

### Phase 2: Core Logic
- [ ] Implement dynamic CSP construction in `src/ibis_profiling/report/report.py`.
- [ ] Verify tests pass (GREEN).

### Phase 3: Verification & Cleanup
- [ ] Run full test suite.
- [ ] Run apples-to-apples benchmark.
- [ ] Execute PE review.
- [ ] Submit PR and merge if benchmarks are reasonable.
