import polars as pl
import ibis.expr.datatypes as dt
from datetime import date
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
    assert result["variables"] == {}


def test_report_to_html():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "a__zeros": 0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    html = report.to_html()

    assert "Ibis Profiling Report" in html
    assert "10.0" in html
    assert "5" in html


def test_report_date_serialization():
    d = date(2023, 1, 1)
    raw_results = pl.DataFrame([{"a__min": d}])
    schema = {"a": dt.Date()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    assert result["variables"]["a"]["min"] == "2023-01-01"


def test_report_structure():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "cat__count": 5, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64(), "cat": dt.String()}

    report = ProfileReport(raw_results, schema)
    # Inject samples to cover _get_sample_section
    report.samples = {"head": {"a": [1, 2, 3]}}

    structure = report.get_structure()
    assert structure.name == "report"
    assert len(structure.items) == 4  # overview, variables, correlations, sample

    # Check variables section
    variables = structure.items[1]
    assert variables.name == "variables"
    assert len(variables.items) == 2  # 'a' and 'cat'

    # Check sample section
    sample = structure.items[3]
    assert sample.name == "sample"
    assert len(sample.items) == 1
