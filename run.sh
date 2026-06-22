#!/usr/bin/env bash
export UV_PROJECT_ENVIRONMENT=/tmp/ibis-profiling/.venv
export XDG_CACHE_HOME=/tmp/ibis-profiling/.cache
export PYTHONPYCACHEPREFIX=/tmp/ibis-profiling/__pycache__
export PATH="/tmp/ibis-profiling/.venv/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/tmp/ibis-profiling/.cache/ms-playwright}"


echo "Using environment: /tmp/ibis-profiling/.venv"
exec "$@"
