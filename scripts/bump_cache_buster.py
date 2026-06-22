#!/usr/bin/env python3
"""Increment the ``?cacheBuster=N`` query params in README.md.

The README embeds remote images (logo, screenshots) and the PyPI version badge via
GitHub's / fury.io's CDNs, which cache aggressively by URL. When the underlying asset
changes (new screenshots, a new published version) the URL is identical, so viewers keep
seeing the stale cached copy. Appending an ever-changing ``?cacheBuster=N`` forces a fresh
fetch. This script bumps every such counter so a release always invalidates the caches.

Usage:
    python scripts/bump_cache_buster.py            # bump every cacheBuster by 1, rewrite README
    python scripts/bump_cache_buster.py --check     # exit 1 if any cacheBuster is present (CI/dry-run); no writes
    python scripts/bump_cache_buster.py --readme path/to/README.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CACHE_BUSTER_RE = re.compile(r"(cacheBuster=)(\d+)")
DEFAULT_README = Path(__file__).resolve().parent.parent / "README.md"


def bump(text: str) -> tuple[str, list[tuple[int, int]]]:
    """Return (new_text, [(old, new), ...]) with every cacheBuster incremented by 1."""
    changes: list[tuple[int, int]] = []

    def _increment(match: re.Match[str]) -> str:
        old = int(match.group(2))
        new = old + 1
        changes.append((old, new))
        return f"{match.group(1)}{new}"

    return CACHE_BUSTER_RE.sub(_increment, text), changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="README path")
    parser.add_argument(
        "--check",
        action="store_true",
        help="report cache-buster params without writing; exit 1 if any are found",
    )
    args = parser.parse_args()

    text = args.readme.read_text(encoding="utf-8")
    new_text, changes = bump(text)

    if not changes:
        print(f"No cacheBuster params found in {args.readme}", file=sys.stderr)
        return 0

    if args.check:
        for old, _ in changes:
            print(f"cacheBuster={old}")
        return 1

    args.readme.write_text(new_text, encoding="utf-8")
    print(f"Bumped {len(changes)} cacheBuster param(s) in {args.readme}:")
    for old, new in changes:
        print(f"  {old} -> {new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
