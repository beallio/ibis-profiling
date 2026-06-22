#!/usr/bin/env python
"""Supply-chain cooldown guard for the vendored esbuild pin.

Fails if the pinned esbuild version (tools/frontend/esbuild.lock.json) was published more
recently than `cooldown_days_required` days ago — mirroring the Python `uv exclude-newer`
security pin for the JS build tool. Run in CI.

Network-tolerant: if the npm registry is unreachable, it WARNS and exits 0 (so offline/air-gapped
builds are not blocked); the pin's integrity is still enforced by SHA256 in bootstrap.sh.
"""

import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

LOCK = Path(__file__).resolve().parent.parent / "tools" / "frontend" / "esbuild.lock.json"


def main() -> int:
    pin = json.loads(LOCK.read_text())
    version = pin["version"]
    required = int(pin["cooldown_days_required"])

    url = f"https://registry.npmjs.org/{pin['npm_package']}"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:  # noqa: S310 (pinned npm registry)
            meta = json.load(resp)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(
            f"WARN: npm registry unreachable ({exc}); skipping cooldown check (SHA256 still enforced)."
        )
        return 0

    published = meta.get("time", {}).get(version)
    if not published:
        print(f"ERROR: npm has no publish time for {pin['npm_package']}@{version}", file=sys.stderr)
        return 1

    pub = dt.datetime.fromisoformat(published.replace("Z", "+00:00"))
    age = (dt.datetime.now(dt.timezone.utc) - pub).days
    print(
        f"esbuild {version}: published {published[:10]} ({age}d ago); cooldown requires >= {required}d"
    )

    if age < required:
        print(
            f"ERROR: pinned esbuild {version} is {age}d old, younger than the {required}d cooldown. "
            f"Pin an older version (and update both SHA256 fields in {LOCK.name}).",
            file=sys.stderr,
        )
        return 1

    # Sanity: published date in the lockfile should match npm.
    if pin.get("published") != published[:10]:
        print(
            f"WARN: lockfile 'published' ({pin.get('published')}) != npm ({published[:10]}).",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
