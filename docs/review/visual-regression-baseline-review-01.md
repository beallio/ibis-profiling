# Review — visual-regression-baseline (round 01, finding 4 Phase 3b-0)

Branch: `feat/visual-regression-baseline` (base `main`). Commit `4848422`.

## Status: CHANGES REQUESTED

The visual oracle is correctly built and STABLE, and the comparison works (a histogram bar recolor
`bg-blue-500/60`->`bg-red-500` correctly fails at 0.031 of pixels differing). Baselines (10 PNGs,
both themes), determinism flags (1920x1080, device_scale_factor=1, reduced_motion, animations
disabled), and the artifact-on-failure output are all good.

**Problem: the tolerance is far too loose.** Measured run-to-run noise floor (identical render vs
baseline, full-page) is **~0.000016** (~33 px / 2.07M). The configured `MAX_DIFF_RATIO = 0.002` is
**125x** that — it lets real visual changes through (a `#3b82f6` sparkline recolor passes). A single
RATIO also misbehaves across image sizes: the same ~33 px of sub-pixel AA noise is a much larger
ratio on a small per-view element crop than on the full page.

## Required changes

1. Replace the ratio threshold with an **absolute per-image pixel budget** `MAX_DIFF_PIXELS`
   (Playwright's `maxDiffPixels` model), so it behaves uniformly for the full-page and the smaller
   element crops. Keep `PIXEL_THRESHOLD = 8` for per-pixel channel sensitivity.
2. Set `MAX_DIFF_PIXELS` to the **smallest value that is stable** — just above the measured noise
   floor. Start at ~150 and confirm: run the test **3 times with zero failures** (no AA false
   positives on any view/theme), tuning down toward ~50 if stable, up only if a view flakes.
3. Re-verify **sensitivity**: a drift check where recoloring the histogram bar class
   (`bg-blue-500/60`) FAILS the affected view. (Fine attribute/stroke changes like the sparkline
   are intentionally caught by the complementary DOM oracle `tests/test_e2e_frontend_snapshot.py`,
   not this one — add a one-line comment in the test documenting this division of labor.)
4. Do NOT loosen `PIXEL_THRESHOLD` or regenerate baselines to make it pass; the baselines are valid.

## Verify after changes

`./run.sh uv run pytest tests/test_e2e_visual_regression.py -q` passes 3x; the histogram-class drift
check fails; `run-quality-gates` green.
