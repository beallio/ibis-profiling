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
#   scripts/release.sh v0.2.0 --notes-file NOTES.md   # custom GitHub Release title+body
#
# --notes-file: the annotated tag message becomes the GitHub Release. release.yml
# reads the tag's first line as the release TITLE and the rest as the BODY (then
# appends auto-generated notes). Without it, the tag message is just the version, so
# the release title is the version and the body is empty. The tag is created with
# `--cleanup=whitespace` so Markdown `#` headings in the notes are preserved (git's
# default `strip` cleanup would delete every line starting with `#`).
set -euo pipefail

version="${1:-}"
dry_run=0
assume_yes=0
notes_file=""
for arg in "${@:2}"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --yes|-y) assume_yes=1 ;;
    --notes-file=*) notes_file="${arg#--notes-file=}" ;;
    --notes-file) echo "error: --notes-file needs a path: --notes-file=PATH" >&2; exit 2 ;;
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

if [[ -n "$notes_file" && ! -f "$notes_file" ]]; then
  echo "error: --notes-file not found: $notes_file" >&2
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
  if [[ -n "$notes_file" ]]; then
    echo "[dry-run]       git tag -a $version --cleanup=whitespace -F $notes_file"
    echo "[dry-run]       (release title = first line of $notes_file; body = the rest)"
  else
    echo "[dry-run]       git tag -a $version -m $version"
  fi
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
if [[ -n "$notes_file" ]]; then
  git tag -a "$version" --cleanup=whitespace -F "$notes_file"
else
  git tag -a "$version" -m "$version"
fi
git push origin "$branch" --follow-tags

echo "Pushed $version. release.yml (GitHub Release) and publish.yml (PyPI) are now running."
