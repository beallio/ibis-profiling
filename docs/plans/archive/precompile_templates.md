# Plan: Pre-compile Templates for Production Performance and Cleanliness

## Problem Definition
The current JIT (Just-In-Time) compilation of JSX and Tailwind CSS causes several issues in production reports:
1. **Security Blocks:** Browsers block Babel's storage access (Tracking Prevention).
2. **Performance:** JIT compilation blocks the main thread, causing long load times and "DOMContentLoaded" violations.
3. **Console Noise:** JIT engines emit "Not for production" warnings.

## Proposed Solution
Implement a **Template Build Process** that pre-compiles JSX and extracts the generated Tailwind CSS.
1. Create a `scripts/build_templates.py` that uses Playwright to load the templates in a "build mode".
2. In this mode, the templates will compile themselves using the JIT engines.
3. The script will then extract the compiled JavaScript and the generated Tailwind CSS from the browser.
4. Save these into "compiled" versions of the templates in `src/ibis_profiling/templates/`.
5. Update `src/ibis_profiling/report/report.py` to use these optimized templates by default.

## Key Files & Context
- `src/ibis_profiling/templates/*.html` (Source templates)
- `src/ibis_profiling/report/report.py` (Template loading logic)
- `scripts/build_templates.py` (New build script)

## Implementation Plan

### Phase 1: Build Infrastructure
- [ ] Create `scripts/build_templates.py`.
- [ ] Implement logic to load templates in Playwright, wait for JIT engines to finish, and extract the resulting code.

### Phase 2: Template Refactoring
- [ ] Split templates into `template_src.html` (source with JSX) and `template.html` (compiled target).
- [ ] Or just automate the overwrite of the standard templates from a separate source folder.

### Phase 3: Integration
- [ ] Run the build script to generate optimized templates.
- [ ] Ensure `report.py` works with the new templates (which will no longer have script tags for Babel or Tailwind JIT).

### Phase 4: Verification
- [ ] Verify that reports generated from optimized templates have zero JIT warnings and no storage blocks.
- [ ] Run full test suite.

## Git Strategy
- Branch: `feat/precompiled-templates`
- Commits:
    - `Add: Template build script using Playwright`
    - `Fix: Optimize templates by pre-compiling JSX and Tailwind`
