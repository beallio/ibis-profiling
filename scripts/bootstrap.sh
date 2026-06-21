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
