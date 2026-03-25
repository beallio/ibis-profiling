import ibis
import pandas as pd
from ibis_profiling import Profiler


def test_empty_dataset_unique():
    """Verify that an empty dataset's columns are not marked as unique."""
    # Create an empty table
    df = pd.DataFrame({"col1": [], "col2": []})
    con = ibis.duckdb.connect()
    t = con.create_table("empty_table", df)

    profiler = Profiler(t)
    report = profiler.run()

    # Empty dataset is NOT unique
    assert report.table["n"] == 0
    assert report.variables["col1"]["is_unique"] is False
    assert report.variables["col2"]["is_unique"] is False


def test_single_row_dataset_unique():
    """Verify that a single-row dataset's columns are marked as unique."""
    df = pd.DataFrame({"col1": [1], "col2": ["A"]})
    con = ibis.duckdb.connect()
    t = con.create_table("single_row_table", df)

    profiler = Profiler(t)
    report = profiler.run()

    # Single-row dataset is unique
    assert report.table["n"] == 1
    assert report.variables["col1"]["is_unique"] is True
    assert report.variables["col2"]["is_unique"] is True
