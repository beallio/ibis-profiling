# Review — visual-regression-baseline (round 02, finding 4 Phase 3b-0)
Branch: `feat/visual-regression-baseline` (base `feat/frontend-modularization`). Commit `4f2c441`.

## Status: APPROVED
CHANGES_REQUESTED addressed: absolute `MAX_DIFF_PIXELS = 350` (was ratio 0.002), `PIXEL_THRESHOLD = 8`,
complementary-DOM-oracle documented. Independently verified: stable 3x (noise floor ~33px << 350);
histogram recolor fails (349,895 px differ); DOM oracle catches fine attribute changes (sparkline);
quality gates green; 10 PNG baselines committed; esbuild binary not committed.

## Oracle stack for Phase 3b (all must pass each round)
DOM snapshot + pixel screenshot (<=350 px) + e2e.
STATUS: APPROVED
