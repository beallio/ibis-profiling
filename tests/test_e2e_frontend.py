import pytest
import pandas as pd
import numpy as np
import ibis
from ibis_profiling import profile


@pytest.fixture(scope="module")
def html_reports(tmp_path_factory):
    """Generates the test HTML reports once for the E2E tests."""
    output_dir = tmp_path_factory.mktemp("e2e_reports")

    # Generate data designed to trigger all components
    np.random.seed(42)
    n = 100
    df = pd.DataFrame(
        {
            "numeric_1": np.random.randn(n),
            "numeric_2": np.random.randn(n) * 10,
            "missing_a": [np.nan if i % 3 == 0 else float(i) for i in range(n)],
            "missing_b": [np.nan if i % 5 == 0 else float(i) for i in range(n)],
            "categorical": np.random.choice(["Alpha", "Beta", "Gamma"], n),
            "boolean": np.random.choice([True, False], n),
        }
    )
    # Correlated column
    df["correlated_col"] = df["numeric_1"] * 2 + np.random.randn(n) * 0.1

    table = ibis.memtable(df)
    report = profile(table, title="E2E Validation Report")

    default_path = output_dir / "default.html"
    ydata_path = output_dir / "ydata.html"

    report.to_file(str(default_path), theme="default")
    report.to_file(str(ydata_path), theme="ydata-like")

    return {
        "default": f"file://{default_path.absolute()}",
        "ydata": f"file://{ydata_path.absolute()}",
    }


def test_default_theme_rendering(page, html_reports):
    """E2E test for the default theme."""
    errors = []
    page.on("pageerror", lambda err: errors.append(f"PageError: {err}"))
    page.on(
        "console",
        lambda msg: errors.append(f"ConsoleError: {msg.text}") if msg.type == "error" else None,
    )

    # Note: Using waitUntil="networkidle" ensures scripts are fully loaded
    page.goto(html_reports["default"], wait_until="networkidle")

    # 1. Root element should render
    page.wait_for_selector("#root", state="visible")

    # 2. Check for basic SVG rendering (e.g. icons, charts)
    page.wait_for_selector("svg", state="visible")

    # 3. Navigate tabs to trigger sub-components rendering
    # Default theme tabs: "Overview", "Variables", "Correlations", "Missing Values"

    # Click Correlations tab (using text matching)
    correlations_tab = page.locator("button:has-text('Correlations')").first
    if correlations_tab.is_visible():
        correlations_tab.click()
        # Ensure we don't crash after clicking
        page.wait_for_selector("text=Correlation Matrix", state="visible", timeout=2000)

    # Click Missing Values tab
    missing_tab = page.locator("button:has-text('Missing Values')").first
    if missing_tab.is_visible():
        missing_tab.click()
        # Verify the matrix or heatmap titles
        page.wait_for_selector("text=Nullity Matrix", state="visible", timeout=2000)

    # Final error check
    assert len(errors) == 0, f"React rendering crashed with errors: {errors}"


def test_ydata_theme_rendering(page, html_reports):
    """E2E test for the ydata-like theme."""
    errors = []
    page.on("pageerror", lambda err: errors.append(f"PageError: {err}"))
    page.on(
        "console",
        lambda msg: errors.append(f"ConsoleError: {msg.text}") if msg.type == "error" else None,
    )

    page.goto(html_reports["ydata"], wait_until="networkidle")

    # 1. Root element
    page.wait_for_selector("#root", state="visible")

    # 2. SVGs should be present
    page.wait_for_selector("svg", state="visible")

    # YData theme uses a vertical sidebar navigation with links like #overview, #variables, #interactions

    # Check if interactions section exists
    interactions_link = page.locator("a[href='#interactions']")
    if interactions_link.is_visible():
        interactions_link.click()
        page.wait_for_selector("text=Interactions", state="visible", timeout=2000)

    # Check correlations
    correlations_link = page.locator("a[href='#correlations']")
    if correlations_link.is_visible():
        correlations_link.click()
        # Wait for the correlation matrix button to appear (e.g. "pearson")
        page.wait_for_selector("button:has-text('pearson')", state="visible", timeout=2000)

    # Check missing values
    missing_link = page.locator("a[href='#missing']")
    if missing_link.is_visible():
        missing_link.click()
        # Wait for the SVG matrix
        page.wait_for_selector("text=Missing Values", state="visible", timeout=2000)

    # Final error check
    assert len(errors) == 0, f"React rendering crashed with errors: {errors}"
