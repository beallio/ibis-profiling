# Plan: Vendor esbuild build tool (finding 4, Phase 2) — DONE

## Context

Finding 4 Phase 2: introduce the frontend build toolchain under the project's dependency-security
policy (see memory: new-dependency-security-cooldown), without yet refactoring the frontend.

Decision (user-approved): **vendored, pinned, SHA256-verified esbuild binary** — not npm. esbuild
has zero transitive deps; React/ReactDOM/Lucide stay vendored UMD globals (marked esbuild
`external`), so the esbuild binary is the *entire* new supply-chain surface. Cooldown ≥ 30 days →
pinned `esbuild 0.28.0` (published 2026-04-02, 80 days old at pin time).

## What was done (committed directly with maintainer-verified checksums)

- `tools/frontend/esbuild.lock.json` — the pin manifest: version, source URL, tarball SHA256,
  npm dist.integrity (sha512), binary SHA256, publish date, required cooldown, install path.
- `scripts/bootstrap.sh` — fetches `@esbuild/linux-x64@0.28.0` from the npm registry, **verifies
  the tarball SHA256**, extracts `package/bin/esbuild`, **verifies the binary SHA256**, installs to
  `/tmp/ibis-profiling/bin/esbuild` (gitignored). Idempotent (skips if the present binary already
  matches the pinned SHA256); aborts on any checksum mismatch.
- `scripts/check_esbuild_cooldown.py` — CI guard: fails if the pinned version is younger than
  `cooldown_days_required`; network-tolerant (warns + exits 0 if npm unreachable, since SHA256
  already enforces integrity).
- `tests/test_frontend_build_tool.py` — verifies the vendored binary matches its pinned SHA256,
  reports `0.28.0`, and bundles JS offline (with `react` kept external). Skips if not provisioned.

## Verified

- esbuild tests: 3 passed (SHA256 match, version, offline bundle). Cooldown guard: PASS (80d ≥ 30d).
  bootstrap idempotent-verify branch: PASS. ruff/ty clean. `run-quality-gates` green (JSON gate 0).
- No binary committed to the repo (lives in `/tmp`); only the manifest + scripts + test.

## Pin-update procedure

Bump `version`, refetch the tarball, recompute + update BOTH `tarball_sha256` and `binary_sha256`
and `published` in the lockfile, update the three constants in `bootstrap.sh`, and confirm
`scripts/check_esbuild_cooldown.py` passes (≥ cooldown). Never adopt a just-published version.

## Follow-up (separate)

origin has **no test-CI workflow** (only publish/release). The cooldown guard, regression-gate
test, esbuild tests, and ruff/ty need a `ci.yml` that bootstraps esbuild + runs them on PRs.

## Next (Phase 3)

Incrementally extract the monolithic inline JSX (`templates/*.src.html`) into modules bundled by the
vendored esbuild, verified at each step against the Phase-1 DOM snapshot oracle
(`tests/test_e2e_frontend_snapshot.py`).
