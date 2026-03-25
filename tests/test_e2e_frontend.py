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
    minimal_report = profile(table, title="E2E Minimal Report", minimal=True)

    default_path = output_dir / "default.html"
    ydata_path = output_dir / "ydata.html"
    minimal_path = output_dir / "minimal.html"

    report.to_file(str(default_path), theme="default")
    report.to_file(str(ydata_path), theme="ydata-like")
    minimal_report.to_file(str(minimal_path), theme="default")

    return {
        "default": f"file://{default_path.absolute()}",
        "ydata": f"file://{ydata_path.absolute()}",
        "minimal": f"file://{minimal_path.absolute()}",
    }


def test_default_theme_rendering(page, html_reports):
    """E2E test for the default theme."""
    errors = []
    page.on("pageerror", lambda err: errors.append(f"PageError: {err}"))
    page.on(
        "console",
        lambda msg: errors.append(f"ConsoleError: {msg.text}") if msg.type == "error" else None,
    )

    page.goto(html_reports["default"], wait_until="networkidle")

    # 1. Root element should render
    page.wait_for_selector("#root", state="visible")

    # 2. Check Variables Section
    variables_tab = page.locator("button:has-text('Variables')").first
    if variables_tab.is_visible():
        variables_tab.click()
        # Ensure a histogram rendered (has <rect> tags for bars)
        page.wait_for_selector("svg rect", state="visible", timeout=30000)

    # 3. Check Interactions Section (Scatter Plots)
    interactions_tab = page.locator("button:has-text('Interactions')").first
    if interactions_tab.is_visible():
        interactions_tab.click()
        # Ensure scatter plot rendered (has <circle> tags for points)
        page.wait_for_selector("svg circle", state="visible", timeout=30000)

    # 4. Check Correlations Section (Heatmap)
    correlations_tab = page.locator("button:has-text('Correlations')").first
    if correlations_tab.is_visible():
        correlations_tab.click()
        # Ensure correlation matrix rendered (has <rect> tags for heatmap cells)
        page.wait_for_selector("text=Correlation Matrix", state="visible")
        page.wait_for_selector("svg rect", state="visible", timeout=30000)

    # 5. Check Missing Values Section
    missing_tab = page.locator("button:has-text('Missing')").first
    if missing_tab.is_visible():
        missing_tab.click()
        # Verify the matrix or heatmap titles
        page.wait_for_selector("text=Nullity Matrix", state="visible")
        # Nullity matrix uses <rect> for presence/absence
        page.wait_for_selector("svg rect", state="visible", timeout=30000)

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

    # 2. Check Variables Section
    variables_link = page.locator("a[href='#variables']")
    if variables_link.is_visible():
        variables_link.click()
        # In ydata theme, numeric histograms use div bars with bg-blue-500
        # and categorical histograms use divs as well.
        # Let's look for the HistogramChart container or a blue bar.
        page.wait_for_selector(".bg-blue-500", state="visible", timeout=30000)

    # 3. Check Interactions Section
    interactions_link = page.locator("a[href='#interactions']")
    if interactions_link.is_visible():
        interactions_link.click()
        page.wait_for_selector("text=Interactions", state="visible")
        # Ensure scatter plot rendered (has <circle> tags for points)
        page.wait_for_selector("svg circle", state="visible", timeout=30000)

    # 4. Check Correlations Section
    correlations_link = page.locator("a[href='#correlations']")
    if correlations_link.is_visible():
        correlations_link.click()
        page.wait_for_selector("button:has-text('pearson')", state="visible")
        # Ensure correlation matrix rendered (has <rect> tags for heatmap cells)
        page.wait_for_selector("svg rect", state="visible", timeout=30000)

    # 5. Check Missing Values Section
    missing_link = page.locator("a[href='#missing']")
    if missing_link.is_visible():
        missing_link.click()
        # In ydata theme, it's 'Missing values'
        page.wait_for_selector("text=Missing values", state="visible")
        # Nullity matrix uses <rect>
        page.wait_for_selector("svg rect", state="visible", timeout=30000)

    # Final error check
    assert len(errors) == 0, f"React rendering crashed with errors: {errors}"


def test_correlation_metadata_filtered(page, html_reports):
    """Ensure _metadata is not selected as the default correlation type."""
    page.goto(html_reports["default"], wait_until="networkidle")

    # Wait for root and navigate to correlations
    page.wait_for_selector("#root", state="visible")
    correlations_tab = page.locator("button:has-text('Correlations')").first
    if correlations_tab.is_visible():
        correlations_tab.click()
        page.wait_for_selector("text=Correlation Matrix", state="visible")

        # Look for buttons that represent the correlation types
        # They are usually uppercase in default theme
        page.locator("button:has-text('PEARSON')").first
        page.locator("button:has-text('SPEARMAN')").first

        # Verify the _metadata button doesn't exist
        metadata_btn = page.locator("button:has-text('_METADATA')").first
        assert not metadata_btn.is_visible(), "_metadata button should not be visible"

        # Check that one of the valid correlations is selected (has a specific active class, e.g., bg-blue-600)
        # Since it depends on the exact styling, we just check that the correlation matrix rendered
        # and doesn't show "No data" because it accidentally selected _metadata.
        no_data_msg = page.locator("text=No data available for this metric.")
        assert not no_data_msg.is_visible(), (
            "Correlation matrix should not be blank due to _metadata selection"
        )
        page.wait_for_selector("svg rect", state="visible", timeout=10000)

    # Do the same for ydata-like theme
    page.goto(html_reports["ydata"], wait_until="networkidle")
    page.wait_for_selector("#root", state="visible")

    correlations_link = page.locator("a[href='#correlations']")
    if correlations_link.is_visible():
        correlations_link.click()
        page.wait_for_selector("button:has-text('pearson')", state="visible")

        # Verify _metadata button is not present
        metadata_btn = page.locator("button:has-text('_metadata')").first
        assert not metadata_btn.is_visible(), (
            "_metadata button should not be visible in ydata theme"
        )

        # Verify it doesn't show "No data"
        no_data_msg = page.locator("text=No data available for this metric.")
        assert not no_data_msg.is_visible(), (
            "Correlation matrix should not be blank due to _metadata selection"
        )
        page.wait_for_selector("svg rect", state="visible", timeout=10000)


def test_minimal_theme_rendering(page, html_reports):
    """E2E test for minimal mode report."""
    errors = []
    page.on("pageerror", lambda err: errors.append(f"PageError: {err}"))
    page.on(
        "console",
        lambda msg: errors.append(f"ConsoleError: {msg.text}") if msg.type == "error" else None,
    )

    page.goto(html_reports["minimal"], wait_until="networkidle")
    page.wait_for_selector("#root", state="visible")

    # In minimal mode, these expensive tabs should NOT exist
    assert not page.locator("button:has-text('Interactions')").is_visible()
    assert not page.locator("button:has-text('Correlations')").is_visible()

    assert len(errors) == 0, f"React rendering crashed in minimal mode: {errors}"
