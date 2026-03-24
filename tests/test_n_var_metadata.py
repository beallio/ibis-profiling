import polars as pl
import ibis.expr.datatypes as dt
from ibis_profiling.report import ProfileReport


def test_n_var_excludes_dataset_metadata():
    """
    Test that n_var counts only real variables and excludes the synthetic '_dataset' entry.
    """
    # Only one real variable 'a'
    raw_results = pl.DataFrame([{"a__mean": 10.0, "_dataset__row_count": 5}])
    # '_dataset' added to schema as metadata
    schema = {"a": dt.Int64(), "_dataset": {"memory_size": 1024, "record_size": 100}}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    # n_var should be 1, not 2
    assert result["table"]["n_var"] == 1
    # Check that it didn't impact p_cells_missing
    # n_cells_missing = 0, n = 5, n_var = 1 -> p_cells_missing = 0.0
    assert result["table"]["p_cells_missing"] == 0.0


def test_p_cells_missing_with_metadata_inflation():
    """
    Test that p_cells_missing calculation uses the correct n_var (excluding metadata).
    """
    # 5 rows, 1 variable 'a', 2 missing values
    # n_cells_missing = 2
    # n = 5, n_var = 1
    # p_cells_missing should be 2 / (5 * 1) = 0.4
    raw_results = pl.DataFrame([{"a__mean": 10.0, "a__n_missing": 2, "_dataset__row_count": 5}])
    schema = {"a": dt.Int64(), "_dataset": {"memory_size": 1024}}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    # Currently it will fail because n_var will be 2
    # p_cells_missing would be 2 / (5 * 2) = 0.2
    assert result["table"]["n_var"] == 1
    assert result["table"]["p_cells_missing"] == 0.4
