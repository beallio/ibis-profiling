#!/usr/bin/env bash
export UV_PROJECT_ENVIRONMENT=/tmp/ibis-profiling/.venv
export XDG_CACHE_HOME=/tmp/ibis-profiling/.cache
export PYTHONPYCACHEPREFIX=/tmp/ibis-profiling/__pycache__
export PATH="/tmp/ibis-profiling/.venv/bin:$PATH"
# Playwright browsers: prefer the project-isolated /tmp cache, but if Chromium isn't
# installed there, fall back to the shared ~/.cache/ms-playwright so the e2e
# visual/DOM-snapshot regression tests actually run in the gate instead of skipping
# (tests/conftest.py skips test_e2e* when no Chromium is found at this path). No
# download here; an externally-set PLAYWRIGHT_BROWSERS_PATH is always respected.
if [ -z "${PLAYWRIGHT_BROWSERS_PATH:-}" ]; then
  _pw_tmp="/tmp/ibis-profiling/.cache/ms-playwright"
  _pw_home="$HOME/.cache/ms-playwright"
  if compgen -G "$_pw_tmp/chromium-*/chrome-linux*/chrome" >/dev/null 2>&1; then
    export PLAYWRIGHT_BROWSERS_PATH="$_pw_tmp"
  elif compgen -G "$_pw_home/chromium-*/chrome-linux*/chrome" >/dev/null 2>&1; then
    export PLAYWRIGHT_BROWSERS_PATH="$_pw_home"
  else
    export PLAYWRIGHT_BROWSERS_PATH="$_pw_tmp"
  fi
fi


echo "Using environment: /tmp/ibis-profiling/.venv"
exec "$@"
