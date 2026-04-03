#!/usr/bin/env bash
export UV_PROJECT_ENVIRONMENT=/tmp/ibis-profiling/.venv
export XDG_CACHE_HOME=/tmp/ibis-profiling/.cache
export PYTHONPYCACHEPREFIX=/tmp/ibis-profiling/__pycache__
export PATH="/tmp/ibis-profiling/.venv/bin:$PATH"

echo "Using environment: /tmp/ibis-profiling/.venv"
exec "$@"
