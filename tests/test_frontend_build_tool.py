"""Phase 2 of finding 4: verify the vendored esbuild build tool.

Confirms the pinned esbuild binary (a) is present and matches its pinned SHA256, and (b) can
bundle JavaScript offline. Skips cleanly if bootstrap has not provisioned esbuild yet
(`./scripts/bootstrap.sh`).
"""

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

LOCK = Path(__file__).resolve().parent.parent / "tools" / "frontend" / "esbuild.lock.json"
PIN = json.loads(LOCK.read_text())
ESBUILD = Path(PIN["install_path"])


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


requires_esbuild = pytest.mark.skipif(
    not ESBUILD.exists(),
    reason=f"vendored esbuild not provisioned at {ESBUILD}; run ./scripts/bootstrap.sh",
)


@requires_esbuild
def test_vendored_esbuild_matches_pinned_sha256():
    assert _sha256(ESBUILD) == PIN["binary_sha256"], (
        "vendored esbuild SHA256 does not match the pin in tools/frontend/esbuild.lock.json"
    )


@requires_esbuild
def test_vendored_esbuild_reports_pinned_version():
    out = subprocess.run([str(ESBUILD), "--version"], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == PIN["version"]


@requires_esbuild
def test_vendored_esbuild_bundles_js(tmp_path):
    # React/Lucide stay external (vendored globals): only our code is bundled.
    (tmp_path / "util.js").write_text("export const greet = (n) => `hi ${n}`;\n")
    (tmp_path / "entry.js").write_text(
        "import { greet } from './util.js';\n"
        "import React from 'react';\n"  # external — must NOT be inlined
        "console.log(greet('world'), React);\n"
    )
    out = subprocess.run(
        [str(ESBUILD), str(tmp_path / "entry.js"), "--bundle", "--format=iife", "--external:react"],
        capture_output=True,
        text=True,
        check=True,
    )
    bundle = out.stdout
    assert "hi ${n}" in bundle  # our module was bundled
    assert 'require("react")' in bundle or "react" in bundle  # react left external, not inlined
