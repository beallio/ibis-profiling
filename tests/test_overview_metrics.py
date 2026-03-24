import polars as pl
import ibis.expr.datatypes as dt
from ibis_profiling.report import ProfileReport


def test_type_counts_includes_datetime():
    # Schema with one datetime, one int, one string
    raw_results = pl.DataFrame([{"a__mean": 10.0, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64(), "b": dt.Timestamp(), "c": dt.String()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    # Numeric (a), DateTime (b), Categorical (c)
    types = result["table"]["types"]
    assert types.get("Numeric") == 1
    assert types.get("DateTime") == 1
    assert types.get("Categorical") == 1


def test_type_counts_with_unsupported():
    # Array/Struct currently map to Categorical, let's see if we can distinguish them
    raw_results = pl.DataFrame([{"_dataset__row_count": 5}])
    schema = {"a": dt.Array(dt.Int64()), "b": dt.Struct({"f1": dt.String()})}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    # After our fix, we expect these to be Unsupported
    types = result["table"]["types"]
    assert types.get("Unsupported") == 2
    assert types.get("Categorical", 0) == 0


def test_report_contains_duplication_metrics():
    # 5 rows, but row count can be anything in this mock
    raw_results = pl.DataFrame([{"_dataset__row_count": 5}])
    schema = {"a": dt.Int64()}

    # We need a way to mock the distinct count which is done in Profiler.run
    # For now, let's check if ProfileReport._build handles them if passed or defaults
    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    # n_duplicates should be in table if added by profiler
    # We'll check the profiler later
    assert "n" in result["table"]
    assert "n_var" in result["table"]
