#!/usr/bin/env bash
files=$(git diff --cached --name-only --diff-filter=ACM | grep "^src/.*\.py$" || true)

for f in $files; do
  base=$(basename "$f" .py)
  test="tests/test_$base.py"
  # Check if standard test or a more specific class-aligned test exists
  if [ ! -f "$test" ] && ! ls tests/test_*$base.py >/dev/null 2>&1; then
    echo "Missing test: $test (or specialized equivalent)"
    exit 1
  fi
done
