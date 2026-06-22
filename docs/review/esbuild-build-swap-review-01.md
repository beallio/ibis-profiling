# Review — esbuild-build-swap (round 01, finding 4 Phase 3a)
Branch: `feat/esbuild-build-swap` (base `refactor/findings-on-trunk`). Commit `267a2b6`.

## Verdict
Approved. Phase 3a (build-mechanism swap, no component split): the inline JSX is extracted verbatim
to `frontend/<theme>/app.jsx`; `scripts/build_templates.py` now compiles via the vendored esbuild
(classic JSX transform, React stays a global) — no Playwright/Babel/pandas/numpy/ibis. Babel CDN
removed from `*.src.html`; `templates/*.html` regenerated.

## Verified — esbuild output renders identically
- `tests/test_e2e_frontend_snapshot.py` + `tests/test_e2e_frontend.py`: 6 passed — rendered DOM is
  byte-identical to the Phase-1 baselines (which were generated from the OLD Babel build), proving
  esbuild output is equivalent. `default.html` changed +475/-1258 (genuine esbuild output) with
  zero rendered-DOM drift.
- `run-quality-gates` green (JSON gate 0; ruff/ty clean). esbuild binary not committed.

## Finalization
`scripts/orchestration/finalize esbuild-build-swap`.
STATUS: APPROVED
