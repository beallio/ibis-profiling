import ibis
import polars as pl
import numpy as np
from ibis_profiling import ProfileReport


def test_missing_matrix_truncation():
    """Verify that missingness matrix is truncated to top-K columns with most missing."""
    n_rows = 100
    n_cols = 60  # Default cap is 50

    data = {}
    for i in range(n_cols):
        # Columns have increasing amounts of missingness
        # col_0 has 1 missing, col_59 has 60 missing
        col_data = np.random.normal(0, 1, n_rows)
        mask = np.zeros(n_rows, dtype=bool)
        mask[: i + 1] = True
        col_data[mask] = np.nan
        data[f"col_{i:02d}"] = col_data

    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    # Max columns = 10 for testing
    report = ProfileReport(table, missing_matrix_max_columns=10)
    desc = report.get_description()

    matrix = desc.get("missing", {}).get("matrix", {})
    columns = matrix.get("matrix", {}).get("columns", [])

    # Verify truncation count
    assert len(columns) == 10

    # Verify prioritization: col_59 should be there, col_0 should not
    assert "col_59" in columns
    assert "col_00" not in columns

    # Verify warning is present
    warnings = desc["analysis"].get("warnings", [])
    assert any("Missingness matrix truncated" in w for w in warnings)
    assert any("out of 60" in w for w in warnings)
    assert any("top 10" in w for w in warnings)


def test_missing_matrix_no_truncation():
    """Verify no truncation occurs if column count is below limit."""
    data = {"a": [1, None, 3], "b": [4, 5, 6]}
    table = ibis.memtable(data)

    report = ProfileReport(table, missing_matrix_max_columns=10)
    desc = report.get_description()

    matrix = desc.get("missing", {}).get("matrix", {})
    columns = matrix.get("matrix", {}).get("columns", [])

    assert len(columns) == 2
    assert "a" in columns
    assert "b" in columns

    # No warning
    warnings = desc["analysis"].get("warnings", [])
    assert not any("Missingness matrix truncated" in w for w in warnings)
