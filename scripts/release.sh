#!/usr/bin/env bash
# Cut a release: bump README cache-busters, commit, tag, push.
#
# Pushing the v* tag triggers .github/workflows/release.yml (GitHub Release +
# auto-generated notes) and publish.yml (build + Trusted-Publish to PyPI). The
# version itself comes from the tag via hatch-vcs, so there is no version file to
# edit. The cache-buster bump must be committed *before* the tag because those
# workflows only read the committed README.
#
# Usage:
#   scripts/release.sh v0.2.0            # interactive, pushes (publishes to PyPI)
#   scripts/release.sh v0.2.0 --dry-run  # read-only: show exactly what would happen
#   scripts/release.sh v0.2.0 --yes      # skip the confirmation prompt
set -euo pipefail

version="${1:-}"
dry_run=0
assume_yes=0
for arg in "${@:2}"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --yes|-y) assume_yes=1 ;;
    *) echo "error: unknown option '$arg'" >&2; exit 2 ;;
  esac
done

if [[ -z "$version" ]]; then
  echo "Usage: $0 vMAJOR.MINOR.PATCH[-rcN] [--dry-run] [--yes]" >&2
  exit 2
fi

if [[ ! "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-(rc|beta|alpha)[0-9]+)?$ ]]; then
  echo "error: version must look like v0.2.0 or v0.2.0-rc1 (got '$version')" >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
branch="$(git rev-parse --abbrev-ref HEAD)"

# --- Preflight ------------------------------------------------------------
if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree not clean; commit or stash before releasing" >&2
  exit 1
fi

if git rev-parse -q --verify "refs/tags/$version" >/dev/null; then
  echo "error: tag $version already exists" >&2
  exit 1
fi

if ! git fetch --quiet origin "$branch" --tags; then
  echo "warning: could not fetch origin/$branch; behind-check uses local refs" >&2
fi
if git rev-parse -q --verify "origin/$branch" >/dev/null &&
  [[ -n "$(git log --oneline "HEAD..origin/$branch" 2>/dev/null || true)" ]]; then
  echo "error: $branch is behind origin/$branch; pull before releasing" >&2
  exit 1
fi

if [[ "$branch" != "main" ]]; then
  echo "warning: releasing from '$branch', not 'main'." >&2
fi

# --- Dry run: read-only preview ------------------------------------------
if [[ "$dry_run" == 1 ]]; then
  echo "[dry-run] release $version from '$branch'"
  echo "[dry-run] cache-busters that would be bumped (+1 each):"
  python3 "$repo_root/scripts/bump_cache_buster.py" --check | sed 's/^/[dry-run]   /' || true
  echo "[dry-run] then: git commit README.md -m 'chore(release): $version'"
  echo "[dry-run]       git tag -a $version -m $version"
  echo "[dry-run]       git push origin $branch --follow-tags  (fires release.yml + publish.yml)"
  exit 0
fi

# --- Confirm (publishes to PyPI, irreversible) ---------------------------
if [[ "$assume_yes" != 1 ]]; then
  read -r -p "Cut $version from '$branch' and publish to PyPI? [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]] || { echo "aborted."; exit 1; }
fi

# --- Execute --------------------------------------------------------------
python3 "$repo_root/scripts/bump_cache_buster.py"
git add README.md
git commit -m "chore(release): $version" -m "Bump README cache-busters so CDN-cached assets and the PyPI badge refresh."
git tag -a "$version" -m "$version"
git push origin "$branch" --follow-tags

echo "Pushed $version. release.yml (GitHub Release) and publish.yml (PyPI) are now running."
