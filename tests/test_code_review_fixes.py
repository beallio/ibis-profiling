import ibis
import polars as pl
import ibis_profiling
from ibis_profiling import ProfileReport


def test_column_with_double_underscores():
    # Test that a column with double underscores is parsed correctly
    # and metrics are properly assigned instead of crashing or mis-assigning.
    df = pl.DataFrame({"user__id__column": [1, 2, 3, 4, 5]})
    t = ibis.memtable(df)

    report = ProfileReport(t, minimal=True)
    report_dict = report.to_dict()

    # Check that the column exists in the variables dictionary
    assert "user__id__column" in report_dict["variables"], (
        "Column with double underscores was not parsed correctly."
    )

    # Check that a metric (e.g., n) was assigned
    metrics = report_dict["variables"]["user__id__column"]
    assert "n" in metrics
    assert metrics["n"] == 5


def test_unhashable_type_value_counts_skipped():
    # Test that Array/Struct types skip the value_counts to avoid crashing
    con = ibis.duckdb.connect()
    t = con.sql("SELECT [1, 2, 3] AS arr_col, 1 AS int_col")

    # Ensure it doesn't crash during execution
    report = ProfileReport(t, minimal=True)
    report_dict = report.to_dict()

    assert "arr_col" in report_dict["variables"]


def test_compute_duplicates_enabled():
    df = pl.DataFrame({"a": [1, 1, 2]})
    t = ibis.memtable(df)

    # Should compute duplicates by default (not minimal)
    report = ProfileReport(t, minimal=False)
    report_dict = report.to_dict()
    assert "n_duplicates" in report_dict["table"]
    assert report_dict["table"]["n_duplicates"] == 1


def test_compute_duplicates_disabled():
    df = pl.DataFrame({"a": [1, 1, 2]})
    t = ibis.memtable(df)

    report = ProfileReport(t, minimal=False, compute_duplicates=False)
    report_dict = report.to_dict()
    assert "n_duplicates" not in report_dict["table"]

    # Ensure warning is added
    assert "Skipped duplicate check as requested." in report_dict["analysis"].get("warnings", [])


def test_schema_not_mutated():
    df = pl.DataFrame({"a": [1, 2, 3]})
    t = ibis.memtable(df)

    profiler = ibis_profiling.Profiler(t)
    profiler.run()

    # Check that _dataset still exists in profiler's original col_types
    assert "_dataset" in profiler.col_types, "_dataset was removed from the profiler col_types"
