#!/usr/bin/env bash
set -Eeuo pipefail

export UV_PROJECT_ENVIRONMENT=/tmp/ibis-profiling/.venv
export XDG_CACHE_HOME=/tmp/ibis-profiling/.cache
export PYTHONPYCACHEPREFIX=/tmp/ibis-profiling/__pycache__
export PATH="/tmp/ibis-profiling/.venv/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/tmp/ibis-profiling/.cache/ms-playwright}"

uv sync

BROWSERS="$PLAYWRIGHT_BROWSERS_PATH"
if ! ls "$BROWSERS"/chromium-*/chrome-linux*/chrome >/dev/null 2>&1; then
    echo "Playwright browsers not found. Installing Chromium..."
    uv run playwright install chromium
else
    echo "Playwright Chromium already present."
fi

# --- Vendored frontend build tool: esbuild (pinned + SHA256-verified) ---
# Pin recorded in tools/frontend/esbuild.lock.json. Zero transitive deps; React/Lucide stay
# vendored UMD globals. Update deliberately (bump version + both checksums + confirm cooldown).
ESBUILD_BIN="/tmp/ibis-profiling/bin/esbuild"
ESBUILD_BIN_SHA256="aafacdf135322bf47c882a4ea4db33d0375583f5b9c3fd2d4e12258e470568be"
ESBUILD_TARBALL_SHA256="e94bf1c7f44197b22cf6a787578eca9af805aa9624104488252de2a765c6a4f0"
ESBUILD_URL="https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-0.28.0.tgz"

esbuild_verified() {
    [[ -x "$ESBUILD_BIN" ]] && printf '%s  %s\n' "$ESBUILD_BIN_SHA256" "$ESBUILD_BIN" | sha256sum -c --status
}

if esbuild_verified; then
    echo "esbuild already present and verified ($("$ESBUILD_BIN" --version))."
else
    echo "Fetching vendored esbuild 0.28.0 (pinned, SHA256-verified)..."
    mkdir -p "$(dirname "$ESBUILD_BIN")"
    _tgz="$(mktemp)"
    curl -fsSL "$ESBUILD_URL" -o "$_tgz"
    printf '%s  %s\n' "$ESBUILD_TARBALL_SHA256" "$_tgz" | sha256sum -c --status \
        || { echo "ERROR: esbuild tarball SHA256 mismatch — refusing to install." >&2; rm -f "$_tgz"; exit 1; }
    _dir="$(mktemp -d)"
    tar -xzf "$_tgz" -C "$_dir" package/bin/esbuild
    install -m 0755 "$_dir/package/bin/esbuild" "$ESBUILD_BIN"
    rm -rf "$_tgz" "$_dir"
    esbuild_verified \
        || { echo "ERROR: esbuild binary SHA256 mismatch after install — removing." >&2; rm -f "$ESBUILD_BIN"; exit 1; }
    echo "esbuild installed + verified ($("$ESBUILD_BIN" --version))."
fi
