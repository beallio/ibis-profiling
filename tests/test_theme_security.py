import polars as pl
import ibis.expr.datatypes as dt
from ibis_profiling.report import ProfileReport


def test_theme_path_traversal_protection():
    """Verify that path traversal attempts in theme selection are blocked."""
    raw_results = pl.DataFrame([{"a__mean": 10.0, "a__zeros": 0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}
    report = ProfileReport(raw_results, schema)

    # Attempt path traversal to reach the LICENSE file in the root directory
    # The templates directory is src/ibis_profiling/templates/
    # From there, ../../../LICENSE should reach the root LICENSE
    traversal_theme = "../../../LICENSE"

    # This should fall back to 'default' and NOT read the LICENSE file
    html = report.to_html(theme=traversal_theme)

    # Verify fallback to default theme
    assert "Ibis Profiling Report" in html

    # Verify warning is recorded
    analysis = report.to_dict()["analysis"]
    assert "warnings" in analysis
    assert any("Invalid theme" in w for w in analysis["warnings"])
    assert traversal_theme in next(w for w in analysis["warnings"] if "Invalid theme" in w)


def test_theme_allowlist_validation():
    """Verify that only allowed themes are used."""
    raw_results = pl.DataFrame([{"a__mean": 10.0, "a__zeros": 0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}
    report = ProfileReport(raw_results, schema)

    # Valid theme
    html = report.to_html(theme="ydata-like")
    assert "Ibis Profiling Report" in html

    # Invalid theme
    invalid_theme = "non-existent-theme"
    html_invalid = report.to_html(theme=invalid_theme)

    # Should fall back to default
    assert "Ibis Profiling Report" in html_invalid

    # Verify warning
    analysis = report.to_dict()["analysis"]
    assert "warnings" in analysis
    assert any(f"Invalid theme '{invalid_theme}'" in w for w in analysis["warnings"])
