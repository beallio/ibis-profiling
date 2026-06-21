# Review — correlation-determinism-fix (round 01, trunk re-apply)
Branch: `feat/correlation-determinism-fix` (base `refactor/findings-on-trunk`). Commit `2fa5312`.

## Verdict
Approved. Seeds the unseeded `table.sample()` in correlations + interactions via `sample_seed=42`
threaded through `profile()`/`Profiler`/`ProfileConfig`. `tests/test_correlation_determinism.py`
proves same-seed reproducibility (and seed-sensitivity) for both sections.

## Gate status
Regression gate 0 differences (it excludes correlations/interactions on this trunk; the determinism
test is the oracle). Quality gates green.

## Finalization
`scripts/orchestration/finalize correlation-determinism-fix`.
STATUS: APPROVED
