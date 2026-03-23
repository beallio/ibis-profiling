import ibis
import pandas as pd
from ibis_profiling import ProfileReport


def test_count_column_robustness():
    """Test that columns named 'count' or 'item_count' don't break top_values detection."""
    df = pd.DataFrame(
        {
            "count": ["A", "A", "B", "C", "C", "C"],
            "item_count": [1, 2, 3, 4, 5, 6],
            "normal": ["X", "Y", "X", "Y", "X", "Y"],
        }
    )
    con = ibis.memtable(df)

    # This should not raise errors during profiling or report generation
    report = ProfileReport(con, title="Robustness Test")

    # Verify top_values for the 'count' column
    # The 'count' column has 3 values: C(3), A(2), B(1)
    variables = report.get_description()["variables"]
    count_stats = variables["count"]

    assert "histogram" in count_stats
    hist = count_stats["histogram"]

    # We expect labels in 'bins' and counts in 'counts'
    # Ibis results are sorted by count descending (from planner.py)
    # C(3), A(2), B(1)
    assert hist["bins"] == ["C", "A", "B"]
    assert hist["counts"] == [3, 2, 1]
