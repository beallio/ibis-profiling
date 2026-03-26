import ibis
import pandas as pd
import numpy as np
from ibis_profiling.report.model.correlations import CorrelationEngine


def test_correlation_zero_variance_logic():
    """Verify constant and all-null columns produce None correlations without NaNs."""
    df = pd.DataFrame(
        {
            "constant": [1.0, 1.0, 1.0, 1.0],
            "all_null": [np.nan, np.nan, np.nan, np.nan],
            "normal": [1.0, 2.0, 3.0, 4.0],
        }
    )

    con = ibis.duckdb.connect()
    t = con.create_table("test_table_zero_var", df)

    # Minimal variables dict for compute_all
    variables = {
        "constant": {"type": "Numeric", "variance": 0.0},
        "all_null": {"type": "Numeric", "variance": 0.0, "n_missing": 4},
        "normal": {"type": "Numeric", "variance": 1.25},
    }

    results = CorrelationEngine.compute_all(t, variables)

    for method in ["pearson", "spearman"]:
        matrix = results[method]["matrix"]
        cols = results[method]["columns"]

        # Verify no NaN/Inf
        for row in matrix:
            for val in row:
                if val is not None:
                    assert not np.isnan(val), f"NaN found in {method} matrix"
                    assert not np.isinf(val), f"Inf found in {method} matrix"

        # constant vs normal should be None (or 0, but our fix emits None via nullif)
        const_idx = cols.index("constant")
        normal_idx = cols.index("normal")
        assert matrix[const_idx][normal_idx] is None, (
            f"Constant column should have None correlation in {method}"
        )

        # all_null vs normal should be None
        null_idx = cols.index("all_null")
        assert matrix[null_idx][normal_idx] is None, (
            f"All-null column should have None correlation in {method}"
        )


if __name__ == "__main__":
    test_correlation_zero_variance_logic()
