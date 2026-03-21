import ibis
import ibis.expr.types as ir
import polars as pl
import unittest.mock as mock
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


def test_empty_table_profiling():
    """Verify that profiling an empty table doesn't crash."""
    import pandas as pd

    df = pd.DataFrame(columns=["a", "b"])
    table = ibis.memtable(df)

    report = profile(table)
    report_dict = report.to_dict()

    assert report_dict["table"]["n"] == 0
    assert "a" in report_dict["variables"]
    assert report_dict["variables"]["a"]["n"] == 0
    assert report_dict["variables"]["a"]["n_missing"] == 0


def test_histogram_failure_warning():
    """Verify that histogram failures are recorded as warnings instead of swallowed."""
    table = ibis.memtable({"a": [1.0, 2.0, 3.0]})

    # We'll mock ibis.expr.types.Table.execute because histograms (value_counts)
    # return a Table, whereas many other setup metrics return Scalars.

    real_execute = ir.Table.execute

    def side_effect(self, *args, **kwargs):
        # We want to fail when it's the histogram calculation.
        # Check for any column containing 'count'.
        if any("count" in str(c).lower() for c in self.columns):
            raise ValueError("Histogram calculation failed!")
        return real_execute(self, *args, **kwargs)

    with mock.patch.object(ir.Table, "execute", autospec=True, side_effect=side_effect):
        report = profile(table)

        # Check that warnings are present in analysis
        assert "warnings" in report.analysis
        assert any("Histogram failed for a" in w for w in report.analysis["warnings"])
        assert "Histogram calculation failed!" in report.analysis["warnings"][0]
