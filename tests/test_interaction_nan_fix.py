import ibis
import pandas as pd
from ibis_profiling.report.model.interactions import InteractionEngine


def test_interaction_scoring_handles_nans():
    """
    Verify that InteractionEngine.compute selects columns correctly even when
    the correlation matrix contains NaNs (e.g., from zero-variance columns).
    """
    # col1 and col3 have strong correlation (-1.0)
    # col2 is constant (zero variance), resulting in NaN correlations
    df = pd.DataFrame({"col1": [1, 2, 3, 4, 5], "col2": [1, 1, 1, 1, 1], "col3": [5, 4, 3, 2, 1]})
    table = ibis.memtable(df)

    variables = {
        "col1": {"type": "Numeric"},
        "col2": {"type": "Numeric"},
        "col3": {"type": "Numeric"},
    }

    # Mock correlations where col2 has NaNs
    correlations = {
        "pearson": {
            "columns": ["col1", "col2", "col3"],
            "matrix": [
                [1.0, float("nan"), -1.0],
                [float("nan"), 1.0, float("nan")],
                [-1.0, float("nan"), 1.0],
            ],
        }
    }

    # We only want top 2 interaction variables
    # Expected: col1 and col3 (because they have high mutual correlation)
    # Actual (before fix): ['col1', 'col2'] due to NaN propagation in scoring
    result = InteractionEngine.compute(
        table, variables, max_interaction_pairs=2, correlations=correlations
    )

    active_cols = result.get("_metadata", {}).get("active_columns", [])

    # This assertion should fail BEFORE the fix
    assert active_cols == ["col1", "col3"]


def test_interaction_scoring_handles_infs():
    """Verify that InteractionEngine.compute handles Infinity values gracefully."""
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": [1, 2, 3], "col3": [1, 2, 4]})
    table = ibis.memtable(df)
    variables = {c: {"type": "Numeric"} for c in df.columns}

    correlations = {
        "pearson": {
            "columns": ["col1", "col2", "col3"],
            "matrix": [[1.0, float("inf"), 0.5], [float("inf"), 1.0, 0.5], [0.5, 0.5, 1.0]],
        }
    }

    result = InteractionEngine.compute(
        table, variables, max_interaction_pairs=2, correlations=correlations
    )
    active_cols = result.get("_metadata", {}).get("active_columns", [])

    # If Inf is treated as 0, then col1/col2 might NOT be selected if col3 has better real correlations.
    # In this case, col3 has 0.5 + 0.5 = 1.0 total.
    # col1 has 0 + 0.5 = 0.5 total.
    # col2 has 0 + 0.5 = 0.5 total.
    # So it should select col3 and one of col1/col2.

    assert "col3" in active_cols
