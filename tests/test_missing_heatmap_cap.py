import ibis
import polars as pl
import numpy as np
from ibis_profiling import ProfileReport


def test_missing_heatmap_truncation():
    """Verify that missingness heatmap is truncated to top-K columns with most missing."""
    n_rows = 100
    n_cols = 30

    data = {}
    for i in range(n_cols):
        # Columns have increasing amounts of missingness
        # col_0 has 1 missing, col_29 has 30 missing
        col_data = np.random.normal(0, 1, n_rows)
        mask = np.zeros(n_rows, dtype=bool)
        mask[: i + 1] = True
        col_data[mask] = np.nan
        data[f"col_{i}"] = col_data

    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    # Max columns = 10
    # Expected: col_29 down to col_20 (the 10 with MOST missing values)
    report = ProfileReport(table, missing_heatmap_max_columns=10)
    desc = report.get_description()

    heatmap = desc.get("missing", {}).get("heatmap", {})
    # Note: heatmap.matrix.matrix is list of dicts in formatted output
    columns = heatmap.get("matrix", {}).get("columns", [])

    assert len(columns) == 10

    # Verify col_29 is present (most missing)
    assert "col_29" in columns
    # Verify col_0 is NOT present (least missing)
    assert "col_0" not in columns

    # Verify warning is present
    warnings = desc["analysis"].get("warnings", [])
    assert any("Missingness heatmap truncated" in w for w in warnings)
    assert any("out of 30" in w for w in warnings)
    assert any("top 10" in w for w in warnings)


def test_missing_heatmap_no_truncation():
    """Verify no truncation occurs if columns with missing are below limit."""
    data = {
        "a": [1, None, 3],
        "b": [None, 2, 3],
        "c": [1, 2, 3],  # no missing, shouldn't be in heatmap
    }
    table = ibis.memtable(data)

    report = ProfileReport(table, missing_heatmap_max_columns=10)
    desc = report.get_description()

    heatmap = desc.get("missing", {}).get("heatmap", {})
    columns = heatmap.get("matrix", {}).get("columns", [])

    assert len(columns) == 2
    assert "a" in columns
    assert "b" in columns
    assert "c" not in columns

    # No warning
    warnings = desc["analysis"].get("warnings", [])
    assert not any("Missingness heatmap truncated" in w for w in warnings)
