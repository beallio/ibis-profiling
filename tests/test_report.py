import polars as pl
import ibis.expr.datatypes as dt
from ibis_profiling.report import ProfileReport


def test_report_building():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    assert result["table"]["n"] == 5
    assert result["variables"]["a"]["mean"] == 10.0
    assert result["variables"]["a"]["type"] == "Numeric"


def test_report_empty_results():
    raw_results = pl.DataFrame([])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    assert result["table"] == {}
    # New behavior: we return initialized variable model even if empty
    assert "a" in result["variables"]
    assert result["variables"]["a"]["n_distinct"] == 0


def test_report_to_html():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "a__zeros": 0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    html = report.to_html()

    assert "Ibis Profiling Report" in html
    assert "10.0" in html
    assert "5" in html


def test_report_themes():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "a__zeros": 0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}
    report = ProfileReport(raw_results, schema)

    # Test default theme
    html_default = report.to_html(theme="default")
    assert "Ibis Profiling Report" in html_default
    assert "Ibis Profiler" in html_default  # Component in default.html

    # Test ydata-like theme
    html_ydata = report.to_html(theme="ydata-like")
    assert "Profiling Report" in html_ydata  # Title in ydata-like.html
    assert "Dataset statistics" in html_ydata

    # Test fallback
    html_fallback = report.to_html(theme="non-existent")
    assert "Ibis Profiling Report" in html_fallback  # Should fallback to default
