import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "src" / "ibis_profiling" / "templates"
FRONTEND_DIR = ROOT / "frontend"
ESBUILD_LOCK = ROOT / "tools" / "frontend" / "esbuild.lock.json"
APP_BUNDLE_MARKER = "<!-- {{APP_BUNDLE}} -->"


def resolve_esbuild() -> Path:
    pin = json.loads(ESBUILD_LOCK.read_text(encoding="utf-8"))
    esbuild = Path(pin["install_path"])
    if not esbuild.is_file():
        print(
            f"esbuild is not installed at {esbuild}; run ./scripts/bootstrap.sh",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return esbuild


def transform_jsx(esbuild: Path, app_path: Path) -> str:
    result = subprocess.run(
        [
            str(esbuild),
            "--loader=jsx",
            "--jsx=transform",
            "--jsx-factory=React.createElement",
            "--jsx-fragment=React.Fragment",
            f"--sourcefile={app_path}",
        ],
        input=app_path.read_text(encoding="utf-8"),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def build_template(template_path: Path, esbuild: Path) -> None:
    theme = template_path.name.removesuffix(".src.html")
    app_path = FRONTEND_DIR / theme / "app.jsx"
    source_html = template_path.read_text(encoding="utf-8")

    if source_html.count(APP_BUNDLE_MARKER) != 1:
        raise ValueError(f"{template_path} must contain exactly one {APP_BUNDLE_MARKER}")
    if not app_path.is_file():
        raise FileNotFoundError(f"missing frontend application source: {app_path}")

    compiled_js = transform_jsx(esbuild, app_path)
    application_script = (
        f'<script nonce="{{{{NONCE}}}}" type="text/javascript">{compiled_js}</script>'
    )
    production_html = source_html.replace(APP_BUNDLE_MARKER, application_script)
    output_path = template_path.with_name(f"{theme}.html")
    output_path.write_text(production_html, encoding="utf-8")
    print(f"Generated {output_path.name}")


def main() -> None:
    esbuild = resolve_esbuild()
    for template_path in sorted(TEMPLATE_DIR.glob("*.src.html")):
        build_template(template_path, esbuild)


if __name__ == "__main__":
    main()
