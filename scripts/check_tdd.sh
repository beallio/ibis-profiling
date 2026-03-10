#!/usr/bin/env bash
files=$(git diff --cached --name-only | grep "^src/.*\.py$" || true)

for f in $files; do
  base=$(basename "$f" .py)
  test="tests/test_$base.py"
  if [ ! -f "$test" ]; then
    echo "Missing test: $test"
    exit 1
  fi
done
