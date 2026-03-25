import ibis
import polars as pl
import numpy as np
from ibis_profiling import ProfileReport


def test_correlations_truncation():
    """Verify that correlations are truncated and the 'best' columns are selected."""
    n_rows = 100

    # good: 0 missing, high variance
    good_cols = {f"good_{i}": np.random.normal(0, 100, n_rows) for i in range(5)}

    # med: 0 missing, medium variance
    med_cols = {f"med_{i}": np.random.normal(0, 10, n_rows) for i in range(5)}

    # bad: 50% missing, high variance
    bad_data = np.random.normal(0, 100, n_rows)
    bad_data[:50] = np.nan
    bad_cols = {f"bad_{i}": bad_data.copy() for i in range(5)}

    # ignore: 0 missing, low variance
    ignore_cols = {f"ignore_{i}": np.random.normal(0, 1, n_rows) for i in range(15)}

    data = {**good_cols, **med_cols, **bad_cols, **ignore_cols}
    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    # Max columns = 15
    # Expected: 5 good, 5 med, 5 ignore (bad should be excluded due to missingness)
    report = ProfileReport(table, correlations_max_columns=15)
    desc = report.get_description()

    corrs = desc.get("correlations", {})
    assert "pearson" in corrs

    # Verify metadata is nested
    assert "_metadata" in corrs
    meta = corrs["_metadata"]
    assert meta["truncated"] is True
    assert meta["original_count"] == 30
    assert meta["limit"] == 15

    # In the formatted output, 'columns' is removed and matrix is list of dicts
    matrix = corrs["pearson"]["matrix"]
    assert len(matrix) == 15

    columns = list(matrix[0].keys())
    assert len(columns) == 15

    # Verify good and med are all there
    for i in range(5):
        assert f"good_{i}" in columns
        assert f"med_{i}" in columns

    # Verify bad are NOT there
    for i in range(5):
        assert f"bad_{i}" not in columns

    # Verify warning is present
    warnings = desc["analysis"].get("warnings", [])
    assert any("Correlations truncated" in w for w in warnings)
    assert any("out of 30" in w for w in warnings)
    assert any("top 15" in w for w in warnings)


def test_correlations_no_truncation():
    """Verify no truncation occurs if columns are below limit."""
    data = {"a": [1, 2, 3], "b": [4, 5, 6]}
    table = ibis.memtable(data)

    report = ProfileReport(table, correlations_max_columns=10)
    desc = report.get_description()

    corrs = desc.get("correlations", {})
    assert "_metadata" in corrs
    assert not corrs["_metadata"].get("truncated")
    # Formatted matrix check
    assert len(corrs["pearson"]["matrix"]) == 2

    assert len(corrs["pearson"]["matrix"][0].keys()) == 2

    warnings = desc["analysis"].get("warnings", [])
    assert not any("Correlations truncated" in w for w in warnings)
