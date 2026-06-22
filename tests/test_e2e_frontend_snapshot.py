import os
import re
from pathlib import Path

import ibis
import numpy as np
import pandas as pd
import pytest

from ibis_profiling import __version__, profile


BASELINE_DIR = Path(__file__).parent / "frontend_baselines"
SECTIONS = ("overview", "variables", "correlations", "missing", "interactions")
DEFAULT_SELECTORS = {
    "variables": "button:has-text('Variables')",
    "correlations": "button:has-text('Correlations')",
    "missing": "button:has-text('Missing')",
    "interactions": "button:has-text('Interactions')",
}
YDATA_SELECTORS = {
    "variables": "a[href='#variables']",
    "correlations": "a[href='#correlations']",
    "missing": "a[href='#missing']",
    "interactions": "a[href='#interactions']",
}


def _normalize(html: str) -> str:
    """Replace volatile rendered values with stable placeholders."""
    normalized = re.sub(r'nonce="[0-9a-f]+"', 'nonce="X"', html)
    normalized = re.sub(
        r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b",
        "DATE",
        normalized,
    )
    normalized = re.sub(r"(Analysis run )[^<]+", r"\1DATE", normalized)
    normalized = re.sub(
        r">\d+(?:\.\d+)?\s*(?:ms|milliseconds?|s|seconds?|secs?)<",
        ">DUR<",
        normalized,
        flags=re.IGNORECASE,
    )
    if __version__:
        normalized = normalized.replace(__version__, "VER")
    normalized = re.sub(r'\s*data-visual-volatile=""', "", normalized)
    return normalized


@pytest.fixture(scope="module")
def snapshot_reports(tmp_path_factory):
    """Generate fixed, seeded reports for both supported themes."""
    output_dir = tmp_path_factory.mktemp("frontend_snapshot_reports")

    np.random.seed(42)
    n = 100
    frame = pd.DataFrame(
        {
            "numeric_1": np.random.randn(n),
            "numeric_2": np.random.randn(n) * 10,
            "missing_a": [np.nan if i % 3 == 0 else float(i) for i in range(n)],
            "missing_b": [np.nan if i % 5 == 0 else float(i) for i in range(n)],
            "categorical": np.random.choice(["Alpha", "Beta", "Gamma"], n),
            "boolean": np.random.choice([True, False], n),
        }
    )
    frame["correlated_col"] = frame["numeric_1"] * 2 + np.random.randn(n) * 0.1

    report = profile(ibis.memtable(frame), title="Snapshot", sample_seed=42)
    paths = {}
    for theme in ("default", "ydata-like"):
        path = output_dir / f"{theme}.html"
        report.to_file(str(path), theme=theme)
        paths[theme] = f"file://{path.absolute()}"
    return paths


def _assert_or_update_snapshot(theme: str, section: str, html: str) -> None:
    baseline_path = BASELINE_DIR / f"{theme}__{section}.html"
    normalized = _normalize(html)

    if os.environ.get("IBIS_UPDATE_SNAPSHOTS") == "1":
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(normalized, encoding="utf-8")
        return

    assert baseline_path.exists(), (
        f"Missing frontend snapshot: {baseline_path}. Regenerate with IBIS_UPDATE_SNAPSHOTS=1."
    )
    assert normalized == baseline_path.read_text(encoding="utf-8"), (
        f"Frontend snapshot drifted: {baseline_path}. "
        "Inspect the pytest diff or regenerate intentionally with "
        "IBIS_UPDATE_SNAPSHOTS=1."
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    ("theme", "selectors"),
    (("default", DEFAULT_SELECTORS), ("ydata-like", YDATA_SELECTORS)),
)
def test_rendered_report_matches_snapshots(page, snapshot_reports, theme, selectors):
    page.goto(snapshot_reports[theme], wait_until="networkidle")
    page.wait_for_selector("#root", state="visible")
    page.wait_for_selector("svg, .bg-blue-500", state="visible", timeout=30000)

    _assert_or_update_snapshot(theme, "overview", page.inner_html("#root"))

    for section in SECTIONS[1:]:
        page.locator(selectors[section]).first.click()
        page.wait_for_timeout(100)
        _assert_or_update_snapshot(theme, section, page.inner_html("#root"))
