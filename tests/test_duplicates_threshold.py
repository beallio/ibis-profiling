import ibis
import pandas as pd
from ibis_profiling import ProfileReport


def test_duplicates_threshold_skipping():
    # 10 rows
    data = {"val": range(10)}
    table = ibis.memtable(pd.DataFrame(data))

    # Threshold < 10, should skip
    report = ProfileReport(table, duplicates_threshold=5)
    description = report.get_description()

    assert description["table"]["n_distinct_rows"] == "Skipped"
    assert description["table"]["n_duplicates"] == "Skipped"
    assert description["table"]["p_duplicates"] == "Skipped"

    # Verify warning is present
    warnings = description["analysis"].get("warnings", [])
    assert any("Skipped duplicate check for large dataset" in w for w in warnings)


def test_duplicates_threshold_forcing():
    # 10 rows
    data = {"val": range(10)}
    table = ibis.memtable(pd.DataFrame(data))

    # Threshold < 10, but compute_duplicates=True, should NOT skip
    report = ProfileReport(table, duplicates_threshold=5, compute_duplicates=True)
    description = report.get_description()

    assert description["table"]["n_distinct_rows"] == 10
    assert description["table"]["n_duplicates"] == 0
    assert description["table"]["p_duplicates"] == 0


def test_duplicates_below_threshold():
    # 10 rows
    data = {"val": range(10)}
    table = ibis.memtable(pd.DataFrame(data))

    # Threshold > 10, should compute
    report = ProfileReport(table, duplicates_threshold=20)
    description = report.get_description()

    assert description["table"]["n_distinct_rows"] == 10
    assert description["table"]["n_duplicates"] == 0
