# Plan: Tighten CSP for HTML Reports

## Problem Definition
The current Content Security Policy (CSP) for HTML reports is too permissive, allowing `'unsafe-inline'`, `'unsafe-eval'`, and `connect-src *`. This weakens protection against Cross-Site Scripting (XSS).

## Architecture Overview
The solution involves:
1. Generating a random, secure nonce for each report generation.
2. Using this nonce for all `<script>` tags instead of allowing `'unsafe-inline'`.
3. Removing `'unsafe-eval'` in offline mode (where pre-compiled templates are used).
4. Restricting `connect-src` based on whether the report is offline or online.

## Core Data Structures
- `csp_directives`: Dynamically constructed based on mode and generated nonce.

## Public Interfaces
- No changes to public interfaces.

## Dependency Requirements
- No new dependencies (uses standard library `secrets`).

## Testing Strategy
- **Functional**: `tests/test_csp_tightening.py` will verify that:
    - CSP meta tag is present and tightened.
    - All script tags have the correct nonce.
    - `'unsafe-inline'` is absent from `script-src`.
    - `'unsafe-eval'` is absent in offline mode.
- **Regression**: Run E2E frontend tests to ensure React app still renders correctly.

## Phased Approach

### Phase 1: Infrastructure & API
- [ ] Create feature branch `fix/tighten-csp`.
- [ ] Create `tests/test_csp_tightening.py`.

### Phase 2: Core Logic (CSP Tightening)
- [ ] Implement nonce generation and dynamic CSP in `src/ibis_profiling/report/report.py`.
- [ ] Update `to_html` to inject nonces into all script tags.
- [ ] Verify `tests/test_csp_tightening.py` passes.

### Phase 3: Verification & Cleanup
- [ ] Run full test suite.
- [ ] Run E2E frontend tests.
- [ ] Run apples-to-apples benchmark.
- [ ] Execute PE review.
- [ ] Submit PR.

## Git Strategy
- Branch: `fix/tighten-csp`
- Commit after each functional step.
