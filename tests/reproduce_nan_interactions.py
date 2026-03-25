import ibis
import pandas as pd
from ibis_profiling.report.model.interactions import InteractionEngine


def test_repro_nan_interactions():
    # Create a table with a zero-variance column
    # col1 has variance, col2 is constant (zero variance), col3 has variance
    df = pd.DataFrame({"col1": [1, 2, 3, 4, 5], "col2": [1, 1, 1, 1, 1], "col3": [5, 4, 3, 2, 1]})
    table = ibis.memtable(df)

    # Mock variables metadata
    variables = {
        "col1": {"type": "Numeric"},
        "col2": {"type": "Numeric"},
        "col3": {"type": "Numeric"},
    }

    # Pearson correlation with constant column will have NaNs
    # col1 and col3 have correlation -1.0
    # col2 with col1 and col3 will have correlation NaN
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

    # We want to see if it handles NaNs gracefully
    # It should probably select col1 and col3 as active_cols if we limit to 2
    result = InteractionEngine.compute(
        table, variables, max_interaction_pairs=2, correlations=correlations
    )

    active_cols = result.get("_metadata", {}).get("active_columns", [])
    print(f"Active columns: {active_cols}")

    # If NaN propagates, col2 might be selected or order might be weird
    # Scores:
    # col1: (abs(NaN) + abs(-1.0)) / 2 = NaN
    # col2: (abs(NaN) + abs(NaN)) / 2 = NaN
    # col3: (abs(-1.0) + abs(NaN)) / 2 = NaN

    # In Python, sorting with NaNs is unstable.
    # [('col1', nan), ('col2', nan), ('col3', nan)] sorted reverse=True
    # might stay as ['col1', 'col2', 'col3'] or some other order.


if __name__ == "__main__":
    test_repro_nan_interactions()
