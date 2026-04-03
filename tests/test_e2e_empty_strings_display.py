import pytest
import ibis
import polars as pl
from ibis_profiling import ProfileReport


@pytest.fixture(scope="module")
def empty_string_reports(tmp_path_factory):
    """Generates reports with empty strings for E2E testing."""
    output_dir = tmp_path_factory.mktemp("empty_reports")

    df = pl.DataFrame(
        {
            "a": ["x", "", "y", "", None],  # 2 empty (40%), 1 missing (20%)
            "b": ["", "", "", "", ""],  # 5 empty (100%)
            "c": ["foo", "bar", "baz", "qux", "quux"],  # 0 empty (0%)
        }
    )
    table = ibis.memtable(df)
    report = ProfileReport(table, title="Empty String E2E Report")

    default_path = output_dir / "default.html"
    ydata_path = output_dir / "ydata.html"

    report.to_file(str(default_path), theme="default")
    report.to_file(str(ydata_path), theme="ydata-like")

    return {
        "default": f"file://{default_path.absolute()}",
        "ydata": f"file://{ydata_path.absolute()}",
    }


def test_empty_strings_display_default(page, empty_string_reports):
    """Verify empty string metrics appear in the default theme."""
    page.goto(empty_string_reports["default"], wait_until="networkidle")
    page.wait_for_selector("#root", state="visible")

    # 1. Overview Stat Card
    page.wait_for_selector("text=Empty Cells", state="visible")
    # Total cells = 15. Empty cells = 7. p_cells_empty = 7/15 = 46.67%
    page.wait_for_selector("text=46.67%", state="visible")

    # 2. Variable Quick View
    page.wait_for_selector("text=40.0% empty", state="visible")
    page.wait_for_selector("text=100.0% empty", state="visible")

    # 3. Variable Details
    variables_tab = page.locator("button:has-text('Variables')").first
    variables_tab.click()
    page.wait_for_selector("text=Empty", state="visible")
    page.wait_for_selector("text=40.00% (2)", state="visible")


def test_empty_strings_display_ydata(page, empty_string_reports):
    """Verify empty string metrics appear in the ydata-like theme."""
    page.goto(empty_string_reports["ydata"], wait_until="networkidle")
    page.wait_for_selector("#root", state="visible")

    # 1. Overview Dataset Statistics
    page.wait_for_selector("text=Empty cells", state="visible")
    page.wait_for_selector("div:has-text('Empty cells') >> text=7", state="visible")
    page.wait_for_selector("div:has-text('Empty cells (%)') >> text=46.7%", state="visible")

    # 2. Variable Card Overview
    page.wait_for_selector("div:has-text('Empty') >> text=2", state="visible")
    page.wait_for_selector("div:has-text('Empty') >> text=40.0%", state="visible")
