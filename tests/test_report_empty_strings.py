import ibis
import polars as pl
from ibis_profiling import ProfileReport


def test_dataset_level_empty_metrics():
    # Create a dataset with known empty strings
    df = pl.DataFrame(
        {
            "a": ["x", "", "y", "", None],  # 2 empty, 1 missing, 2 present
            "b": ["", "", "", "", ""],  # 5 empty
            "c": [1, 2, 3, 4, 5],  # 0 empty
        }
    )
    table = ibis.memtable(df)

    report = ProfileReport(table)
    desc = report.get_description()

    table_stats = desc["table"]
    var_stats = desc["variables"]

    # Dataset level
    n_var = len(table.columns)
    assert n_var == 3

    # n_cells_empty = 2 (a) + 5 (b) = 7
    assert table_stats["n_cells_empty"] == 7

    # n_vars_with_empty = 2 (a and b)
    assert table_stats["n_vars_with_empty"] == 2

    # p_cells_empty = 7 / (5 * 3) = 7 / 15 = 0.4666...
    assert abs(table_stats["p_cells_empty"] - 7 / 15) < 1e-6

    # Variable level
    assert var_stats["a"]["n_empty"] == 2
    assert abs(var_stats["a"]["p_empty"] - 0.4) < 1e-6

    assert var_stats["b"]["n_empty"] == 5
    assert var_stats["b"]["p_empty"] == 1.0

    assert var_stats["c"].get("n_empty", 0) == 0
