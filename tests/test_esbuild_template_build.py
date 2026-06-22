"""Contract tests for the static esbuild template build."""

import ast
import json
from pathlib import Path

import pytest

from scripts import build_templates

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "src" / "ibis_profiling" / "templates"
FRONTEND_DIR = ROOT / "frontend"
ESBUILD_LOCK = ROOT / "tools" / "frontend" / "esbuild.lock.json"
THEMES = ("default", "ydata-like")


def test_template_sources_use_extracted_app_bundles():
    for theme in THEMES:
        app_source = (FRONTEND_DIR / theme / "app.jsx").read_text()
        template_source = (TEMPLATE_DIR / f"{theme}.src.html").read_text()

        assert app_source.strip()
        assert template_source.count("<!-- {{APP_BUNDLE}} -->") == 1
        assert 'type="text/babel"' not in template_source
        assert "@babel/standalone" not in template_source


def test_template_builder_has_no_browser_or_report_runtime_dependencies():
    build_script = ROOT / "scripts" / "build_templates.py"
    tree = ast.parse(build_script.read_text())
    imported_modules = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert imported_modules.isdisjoint({"playwright", "pandas", "numpy", "ibis", "ibis_profiling"})


def test_template_builder_transforms_jsx_with_vendored_esbuild(tmp_path):
    esbuild = Path(json.loads(ESBUILD_LOCK.read_text())["install_path"])
    if not esbuild.is_file():
        pytest.skip("run ./scripts/bootstrap.sh to provision vendored esbuild")
    app_path = tmp_path / "app.jsx"
    app_path.write_text("const view = <main>Report</main>;\n")

    compiled = build_templates.transform_jsx(esbuild, app_path)

    assert 'React.createElement("main", null, "Report")' in compiled
