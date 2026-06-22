import io
import os
from pathlib import Path

import ibis
import numpy as np
import pandas as pd
import pytest
from PIL import Image, ImageChops

from ibis_profiling import profile


BASELINE_DIR = Path(__file__).parent / "visual_baselines"
ARTIFACT_DIR = Path("/tmp/ibis-profiling/visual_artifacts")
PIXEL_THRESHOLD = 8
MAX_DIFF_RATIO = 0.002
VIEWS = ("variables", "correlations", "interactions", "missing")
DEFAULT_NAV = {
    "variables": "button:has-text('Variables')",
    "correlations": "button:has-text('Correlations')",
    "interactions": "button:has-text('Interactions')",
    "missing": "button:has-text('Missing')",
}
YDATA_NAV = {
    "variables": "a[href='#variables']",
    "correlations": "a[href='#correlations']",
    "interactions": "a[href='#interactions']",
    "missing": "a[href='#missing']",
}


@pytest.fixture(scope="module")
def visual_reports(tmp_path_factory):
    """Generate fixed, seeded reports for both supported themes."""
    output_dir = tmp_path_factory.mktemp("visual_regression_reports")

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

    report = profile(ibis.memtable(frame), title="Visual", sample_seed=42)
    paths = {}
    for theme in ("default", "ydata-like"):
        path = output_dir / f"{theme}.html"
        report.to_file(str(path), theme=theme)
        paths[theme] = f"file://{path.absolute()}"
    return paths


def _assert_or_update_baseline(theme: str, view: str, actual_png: bytes) -> None:
    baseline_path = BASELINE_DIR / f"{theme}__{view}.png"

    if os.environ.get("IBIS_UPDATE_VISUAL_BASELINES") == "1":
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        baseline_path.write_bytes(actual_png)
        return

    assert baseline_path.exists(), (
        f"Missing visual baseline: {baseline_path}. Regenerate with IBIS_UPDATE_VISUAL_BASELINES=1."
    )

    with (
        Image.open(baseline_path) as baseline_source,
        Image.open(io.BytesIO(actual_png)) as actual_source,
    ):
        baseline = baseline_source.convert("RGB")
        actual = actual_source.convert("RGB")

    assert actual.size == baseline.size, (
        f"Visual size drifted for {baseline_path}: expected {baseline.size}, got {actual.size}."
    )

    channel_differences = ImageChops.difference(actual, baseline).split()
    max_channel_difference = ImageChops.lighter(
        ImageChops.lighter(channel_differences[0], channel_differences[1]),
        channel_differences[2],
    )
    threshold_mask = max_channel_difference.point(
        [0 if value <= PIXEL_THRESHOLD else 255 for value in range(256)]
    )
    differing = threshold_mask.histogram()[255]
    diff = Image.new("RGB", actual.size, "black")
    diff.paste((255, 0, 0), mask=threshold_mask)

    total = actual.width * actual.height
    ratio = differing / total
    if ratio > MAX_DIFF_RATIO:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        actual_path = ARTIFACT_DIR / f"{theme}__{view}.actual.png"
        diff_path = ARTIFACT_DIR / f"{theme}__{view}.diff.png"
        actual.save(actual_path)
        diff.save(diff_path)
        pytest.fail(
            f"Visual drift for {baseline_path}: {ratio:.6f} of pixels differ "
            f"(maximum {MAX_DIFF_RATIO:.6f}); actual={actual_path}; diff={diff_path}"
        )


def _navigate_to_view(page, theme: str, view: str):
    nav = DEFAULT_NAV if theme == "default" else YDATA_NAV
    page.locator(nav[view]).first.click()

    if theme == "default":
        selectors = {
            "variables": "h4:has-text('Distribution Overview') + div",
            "correlations": "table.min-w-max.border-collapse",
            "interactions": "svg[viewBox='0 0 800 400']",
            "missing": "svg[viewBox='0 0 1000 400']",
        }
        target = page.locator(selectors[view]).first
    else:
        selectors = {
            "variables": "#variables div.flex.items-end.h-40",
            "correlations": "#correlations table",
            "interactions": "#interactions svg[viewBox='0 0 800 600']",
            "missing": "#missing svg[viewBox='0 0 1000 400']",
        }
        target = page.locator(selectors[view]).first

    target.wait_for(state="visible", timeout=30000)
    target.scroll_into_view_if_needed()
    page.wait_for_timeout(100)
    return target


@pytest.mark.slow
@pytest.mark.parametrize("theme", ("default", "ydata-like"))
def test_report_matches_visual_baselines(browser, visual_reports, theme):
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=1,
        reduced_motion="reduce",
    )
    page = context.new_page()
    try:
        page.goto(visual_reports[theme], wait_until="networkidle")
        page.add_style_tag(
            content=(
                "* { animation: none !important; transition: none !important; "
                "caret-color: transparent !important; }"
            )
        )
        page.wait_for_selector("#root", state="visible")

        _navigate_to_view(page, theme, "variables")
        _assert_or_update_baseline(theme, "full-page", page.screenshot(full_page=True))

        for view in VIEWS:
            target = _navigate_to_view(page, theme, view)
            _assert_or_update_baseline(theme, view, target.screenshot())
    finally:
        context.close()
