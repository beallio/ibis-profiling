import polars as pl
import ibis.expr.datatypes as dt
from ibis_profiling.report import ProfileReport


def test_report_building():
    raw_results = pl.DataFrame([{"a__mean": 10.0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    assert result["dataset"]["row_count"] == 5
    assert result["columns"]["a"]["mean"] == 10.0
    assert result["columns"]["a"]["type"] == str(dt.Int64())
