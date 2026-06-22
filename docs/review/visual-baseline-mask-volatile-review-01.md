# Review — visual-baseline-mask-volatile (round 01, finding 4 Phase 3b-0 fix)
Branch: `feat/visual-baseline-mask-volatile` (base `feat/frontend-modularization`). Commit `8a1de51`.

## Status: APPROVED
Fixes the non-deterministic full-page visual screenshots. The default theme's volatile "Analysis
run <date>" + "Job Duration" elements are tagged `data-visual-volatile=""` and masked in the
full-page screenshot; ydata-like renders no volatile date/duration (static footer only) so needs
none. The DOM snapshot `_normalize` strips the new attribute so DOM baselines are unchanged.

## Independently verified (full-suite, across runs — the gap in the prior review)
- `./run.sh uv run pytest` (WHOLE suite) green THREE times at ~80s spacing (different timestamps):
  235 passed, 1 skipped each. The date/duration no longer cause drift.
- Sensitivity intact: histogram bar recolor still fails (349,634 px differ >> 350); the mask covers
  only the date/duration, charts remain fully pixel-compared.
- `run-quality-gates` green; only `*full-page.png` baselines changed; esbuild binary not committed.

## Finalization
`scripts/orchestration/finalize visual-baseline-mask-volatile` (into feat/frontend-modularization).
STATUS: APPROVED
