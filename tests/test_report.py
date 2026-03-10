import polars as pl
import ibis.expr.datatypes as dt
from datetime import date
from ibis_profiling.report import ProfileReport


def test_report_building():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    assert result["dataset"]["row_count"] == 5
    assert result["columns"]["a"]["mean"] == 10.0
    assert result["columns"]["a"]["type"] == str(dt.Int64())


def test_report_empty_results():
    raw_results = pl.DataFrame([])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    assert result["dataset"] == {}
    assert result["columns"] == {}


def test_report_to_html():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "a__zeros": 0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    html = report.to_html()

    assert "<h1>Data Profile Report</h1>" in html
    assert "<td>a</td>" in html
    assert "<td>10.0</td>" in html
    assert "<td>5</td>" in html


def test_report_date_serialization():
    d = date(2023, 1, 1)
    raw_results = pl.DataFrame([{"a__min": d}])
    schema = {"a": dt.Date()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    assert result["columns"]["a"]["min"] == "2023-01-01"
