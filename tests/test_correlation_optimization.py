import ibis
import pandas as pd
import pytest
from ibis_profiling.report.model.correlations import CorrelationEngine
from ibis_profiling.report.model.missing import MissingEngine


def test_pearson_symmetry_and_diagonal():
    # Create a small dataset with known correlations
    df = pd.DataFrame(
        {
            "a": [1, 2, 3, 4, 5],
            "b": [5, 4, 3, 2, 1],  # -1.0 correlation with a
            "c": [1, 2, 1, 2, 1],  # Some other correlation
        }
    )
    con = ibis.duckdb.connect()
    table = con.create_table("corr_test", df, temp=True)

    results = CorrelationEngine.compute_all(table, variables={}, max_columns=10)
    pearson = results["pearson"]["matrix"]

    # Check dimensions
    assert len(pearson) == 3
    assert len(pearson[0]) == 3

    # Check diagonal
    for i in range(3):
        assert pearson[i][i] == pytest.approx(1.0)

    # Check symmetry and specific values
    # a vs b
    assert pearson[0][1] == pytest.approx(-1.0)
    assert pearson[1][0] == pytest.approx(-1.0)

    # a vs c
    assert pearson[0][2] == pytest.approx(pearson[2][0])

    # b vs c
    assert pearson[1][2] == pytest.approx(pearson[2][1])


def test_missing_heatmap_symmetry():
    # Create dataset with missing values
    df = pd.DataFrame(
        {"a": [1, 2, None, 4, 5], "b": [None, 4, 3, 2, 1], "c": [1, None, None, 2, 1]}
    )
    con = ibis.duckdb.connect()
    table = con.create_table("missing_test", df, temp=True)

    # We need to provide n_missing in variables for MissingEngine
    variables = {
        "a": {"n_missing": 1, "n": 5},
        "b": {"n_missing": 1, "n": 5},
        "c": {"n_missing": 2, "n": 5},
    }

    results = MissingEngine.compute(table, variables)
    heatmap = results["heatmap"]["matrix"]["matrix"]

    # Check dimensions (3 columns with missing values)
    assert len(heatmap) == 3

    # Check symmetry and diagonal
    for i in range(3):
        assert heatmap[i][i] == pytest.approx(1.0)
        for j in range(3):
            assert heatmap[i][j] == pytest.approx(heatmap[j][i])


if __name__ == "__main__":
    pytest.main([__file__])
