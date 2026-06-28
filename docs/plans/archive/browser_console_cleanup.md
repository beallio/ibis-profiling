# Plan: Address Browser Console Warnings and Security Blocks

## Problem Definition
The generated reports show several warnings and errors in the browser console:
1. **Tracking Prevention:** Edge/Chrome block storage access for `unpkg.com` scripts (Babel).
2. **Production Warnings:** `cdn.tailwindcss.com` and `babel-standalone` emit console warnings because they are intended for development use.
3. **Performance Violations:** In-browser compilation of large JSX blocks blocks the main thread, causing "DOMContentLoaded violation" warnings.

## Proposed Solution
1. **Script Isolation:** Add `crossorigin="anonymous"` to all CDN script tags to improve security isolation and potentially bypass some tracking prevention logic.
2. **Warning Suppression:** Inject a small script to temporarily suppress known JIT-related console warnings during the initialization phase.
3. **CDN Diversification:** Switch from `unpkg.com` to `cdnjs.cloudflare.com` for Babel to see if it improves the tracking prevention status in Edge.
4. **Performance:** While true pre-compilation is the best fix, for now, we will focus on console cleanliness and security isolation.

## Key Files & Context
- `src/ibis_profiling/templates/default.html`
- `src/ibis_profiling/templates/ydata-like.html`

## Implementation Plan

### Phase 1: Update Script Tags
- [ ] Add `crossorigin="anonymous"` to Tailwind, Babel, React, ReactDOM, and Lucide script tags.
- [ ] Switch Babel to `cdnjs` build.

### Phase 2: Implement Warning Suppression
- [ ] Add a small inline `<script>` at the top of `<head>` that filters out the "production" warnings from Tailwind and Babel.

### Phase 3: Verification
- [ ] Generate a report and open in Edge.
- [ ] Verify the console is "clean" of these specific warnings.

## Git Strategy
- Branch: `fix/browser-console-cleanup`
- Commits:
    - `Fix: Add crossorigin and switch to cdnjs for better browser compatibility`
    - `Fix: Suppress JIT-related production warnings in browser console`
