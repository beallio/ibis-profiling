import ibis
import pandas as pd
from datetime import datetime
from ibis_profiling import profile


def test_basic_profile():
    con = ibis.duckdb.connect()
    t = con.sql("SELECT 1 AS id, 'a' AS txt").to_pandas()
    table = ibis.memtable(t)

    report = profile(table)

    assert "dataset" in report
    assert "columns" in report
    assert "id" in report["columns"]
    assert "txt" in report["columns"]
    assert report["dataset"]["row_count"] == 1


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
    df = pd.DataFrame(data)
    table = ibis.memtable(df)

    report = profile(table)

    # Dataset stats
    assert report["dataset"]["row_count"] == 4

    # Integer column
    int_stats = report["columns"]["int_col"]
    assert int_stats["missing"] == 1
    assert int_stats["unique"] == 3
    assert int_stats["min"] == 1
    assert int_stats["max"] == 3
    assert int_stats["mean"] == 2.0

    # String column
    str_stats = report["columns"]["str_col"]
    assert str_stats["unique"] == 3
    assert "mean" not in str_stats  # Should not have mean for string

    # Date column
    date_stats = report["columns"]["date_col"]
    assert date_stats["min"] == datetime(2023, 1, 1)
    assert date_stats["max"] == datetime(2023, 1, 4)
