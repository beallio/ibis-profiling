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
    entrypoints = {
        "default": FRONTEND_DIR / "default" / "index.jsx",
        "ydata-like": FRONTEND_DIR / "ydata-like" / "index.jsx",
    }

    for theme, entrypoint in entrypoints.items():
        app_source = entrypoint.read_text()
        template_source = (TEMPLATE_DIR / f"{theme}.src.html").read_text()

        assert app_source.strip()
        assert template_source.count("<!-- {{APP_BUNDLE}} -->") == 1
        assert 'type="text/babel"' not in template_source
        assert "@babel/standalone" not in template_source


def test_ydata_frontend_uses_foundation_modules():
    ydata_frontend = FRONTEND_DIR / "ydata-like"
    index_source = (ydata_frontend / "index.jsx").read_text()

    assert not (ydata_frontend / "app.jsx").exists()
    assert 'import { REPORT_DATA } from "./data.js";' in index_source
    assert 'from "./helpers.js";' in index_source

    component_names = (
        "TypeIcon",
        "HistogramChart",
        "StatRow",
        "NullityMatrix",
        "CorrelationMatrixComponent",
        "ScatterPlot",
    )
    for component_name in component_names:
        component_path = ydata_frontend / "components" / f"{component_name}.jsx"
        component_source = component_path.read_text()

        assert f'from "./components/{component_name}.jsx";' in index_source
        assert f"export const {component_name}" in component_source
        assert f"const {component_name}" not in index_source
        assert 'from "react"' not in component_source

    for section_name in (
        "OverviewSection",
        "VariableDetails",
        "VariableCard",
        "MissingValuesSection",
        "CorrelationsSection",
        "SampleSection",
        "InteractionsSection",
    ):
        assert f"const {section_name}" in index_source

    assert "function App()" in index_source


def test_default_frontend_uses_modular_app_shell():
    default_frontend = FRONTEND_DIR / "default"
    index_source = (default_frontend / "index.jsx").read_text()
    app_source = (default_frontend / "App.jsx").read_text()
    app_content_source = (default_frontend / "AppContent.jsx").read_text()

    assert index_source.strip() == (
        'import { App } from "./App.jsx";\n\n'
        "const root = ReactDOM.createRoot(document.getElementById('root'));\n"
        "root.render(<App />);"
    )
    assert "export function App()" in app_source
    assert 'import { AppContent } from "./AppContent.jsx";' in app_source
    assert "export function AppContent()" in app_content_source
    assert "function AppContent()" not in index_source
    assert "function App()" not in index_source
    assert 'from "react"' not in app_source
    assert 'from "react"' not in app_content_source


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


def test_template_builder_bundles_module_entrypoint(monkeypatch, tmp_path):
    frontend_dir = tmp_path / "frontend"
    theme_dir = frontend_dir / "default"
    theme_dir.mkdir(parents=True)
    index_path = theme_dir / "index.jsx"
    index_path.write_text(
        'import { label } from "./constants.js";\nconst view = <main>{label}</main>;\n'
    )
    (theme_dir / "constants.js").write_text('export const label = "Report";\n')

    template_path = tmp_path / "default.src.html"
    template_path.write_text("<body><!-- {{APP_BUNDLE}} --></body>")
    calls = []

    monkeypatch.setattr(build_templates, "FRONTEND_DIR", frontend_dir)
    monkeypatch.setattr(
        build_templates,
        "bundle_jsx",
        lambda esbuild, entrypoint: calls.append((esbuild, entrypoint)) or "bundled();\n",
    )
    monkeypatch.setattr(
        build_templates,
        "transform_jsx",
        lambda *_args: pytest.fail("module entrypoint must use the bundle path"),
    )

    esbuild = tmp_path / "esbuild"
    build_templates.build_template(template_path, esbuild)

    assert calls == [(esbuild, index_path)]
    assert "bundled();" in (tmp_path / "default.html").read_text()


def test_template_builder_falls_back_to_single_file_transform(monkeypatch, tmp_path):
    frontend_dir = tmp_path / "frontend"
    theme_dir = frontend_dir / "ydata-like"
    theme_dir.mkdir(parents=True)
    app_path = theme_dir / "app.jsx"
    app_path.write_text("const view = <main>Report</main>;\n")

    template_path = tmp_path / "ydata-like.src.html"
    template_path.write_text("<body><!-- {{APP_BUNDLE}} --></body>")
    calls = []

    monkeypatch.setattr(build_templates, "FRONTEND_DIR", frontend_dir)
    monkeypatch.setattr(
        build_templates,
        "bundle_jsx",
        lambda *_args: pytest.fail("single-file source must use the transform fallback"),
        raising=False,
    )
    monkeypatch.setattr(
        build_templates,
        "transform_jsx",
        lambda esbuild, source: calls.append((esbuild, source)) or "transformed();\n",
    )

    esbuild = tmp_path / "esbuild"
    build_templates.build_template(template_path, esbuild)

    assert calls == [(esbuild, app_path)]
    assert "transformed();" in (tmp_path / "ydata-like.html").read_text()
