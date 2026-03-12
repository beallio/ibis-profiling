import ibis
import polars as pl
from datetime import datetime
from ibis_profiling import profile


def test_basic_profile():
    con = ibis.duckdb.connect()
    t = con.sql("SELECT 1 AS id, 'a' AS txt").to_polars()
    table = ibis.memtable(t)

    report_obj = profile(table)
    report = report_obj.to_dict()

    assert "table" in report
    assert "variables" in report
    assert "id" in report["variables"]
    assert "txt" in report["variables"]
    assert report["table"]["n"] == 1


def test_complex_profile():
    data = {
        "int_col": [1, 2, 3, None],
        "float_col": [1.1, 2.2, 3.3, 4.4],
        "str_col": ["a", "b", "c", "a"],
        "date_col": [
            datetime(2023, 1, 1),
            datetime(2023, 1, 2),
            datetime(2023, 1, 3),
            datetime(2023, 1, 4),
        ],
    }
    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    report_obj = profile(table)
    report = report_obj.to_dict()

    # Dataset stats
    assert report["table"]["n"] == 4

    # Integer column
    int_stats = report["variables"]["int_col"]
    assert int_stats["n_missing"] == 1
    assert int_stats["n_distinct"] == 3
    assert int_stats["n_unique"] == 3  # All are singletons in this sample [1, 2, 3]
    assert int_stats["min"] == 1
    assert int_stats["max"] == 3
    assert int_stats["mean"] == 2.0

    # String column
    str_stats = report["variables"]["str_col"]
    assert str_stats["n_distinct"] == 3
    assert str_stats["n_unique"] == 2  # 'a' is not a singleton
    assert "mean" not in str_stats  # Should not have mean for string

    # Date column
    date_stats = report["variables"]["date_col"]
    assert date_stats["min"] == "2023-01-01T00:00:00"
    assert date_stats["max"] == "2023-01-04T00:00:00"


def test_profilereport_wrapper():
    import polars as pl
    from datetime import datetime

    data = {
        "id": range(100),
        "val_numeric": [float(i) if i % 10 != 0 else None for i in range(100)],
        "val_zeros": [0 if i % 5 == 0 else i for i in range(100)],
        "val_categorical": ["A" if i % 3 == 0 else "B" for i in range(100)],
        "val_bool": [True if i % 2 == 0 else False for i in range(100)],
        "val_datetime": [datetime(2023, 1, 1) for _ in range(100)],
        "val_constant": ["fixed"] * 100,
        "val_skewed": [1.0] * 95 + [1000.0] * 5,
        "corr_base": [float(i) for i in range(100)],
        "corr_high": [float(i) * 2 + 5 for i in range(100)],
    }
    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    from ibis_profiling import ProfileReport

    report = ProfileReport(table)

    # Test ydata-style API
    assert isinstance(report.to_dict(), dict)
    assert isinstance(report.get_description(), dict)
    assert "id" in report.get_description()["variables"]

    # Test file export (minimal check)
    import os

    output_html = "/tmp/ibis-profiling/test_export.html"
    output_json = "/tmp/ibis-profiling/test_export.json"

    # Cleanup if exists
    if os.path.exists(output_html):
        os.remove(output_html)
    if os.path.exists(output_json):
        os.remove(output_json)

    report.to_file(output_html)
    assert os.path.exists(output_html)

    report.to_file(output_json)
    assert os.path.exists(output_json)
