import ibis
import pandas as pd
from ibis_profiling import profile
from ibis_profiling.report.model.interactions import InteractionEngine


def test_interactions_computation():
    # Create a small table with numeric columns
    data = {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [5.0, 4.0, 3.0, 2.0, 1.0],
        "z": [10.0, 20.0, 30.0, 40.0, 50.0],
        "cat": ["a", "b", "c", "d", "e"],
    }
    table = ibis.memtable(data)

    # Run profile with minimal=False to trigger interactions
    report = profile(table, minimal=False)
    report_dict = report.to_dict()

    # Check if interactions exist in the report
    assert "interactions" in report_dict
    interactions = report_dict["interactions"]

    # We expect interactions between numeric columns: (x, y), (x, z), (y, z)
    # The structure should be interactions[col1][col2] = list of points
    assert "x" in interactions
    assert "y" in interactions["x"]
    assert "z" in interactions["x"]

    # Check data points for x and y
    points = interactions["x"]["y"]
    assert len(points) == 5
    # Each point should be a dict with x and y values
    # Note: Ibis may return float values, and dict order might vary,
    # but since it's a small memtable, order should be preserved.
    assert points[0]["x"] == 1.0
    assert points[0]["y"] == 5.0


def test_interaction_engine_symmetry():
    """Verify that InteractionEngine computes all pairs correctly and symmetrically."""
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [5, 4, 3, 2, 1], "c": [1, 1, 1, 1, 1]})
    table = ibis.memtable(df)

    # numeric_cols are ['a', 'b', 'c']
    variables = {"a": {"type": "Numeric"}, "b": {"type": "Numeric"}, "c": {"type": "Numeric"}}
    numeric_cols = list(variables.keys())

    # Original compute
    interactions = InteractionEngine.compute(table, variables)

    # Check that interactions[a][b] exists and is the same as interactions[b][a] (swapped)
    assert "a" in interactions
    assert "b" in interactions["a"]
    assert "b" in interactions
    assert "a" in interactions["b"]

    ab = interactions["a"]["b"]
    ba = interactions["b"]["a"]

    assert len(ab) == len(ba)
    for p_ab, p_ba in zip(ab, ba):
        assert p_ab["x"] == p_ba["y"]
        assert p_ab["y"] == p_ba["x"]

    # Check that all pairs (A,B) where A != B are present
    for c1 in numeric_cols:
        for c2 in numeric_cols:
            if c1 != c2:
                assert c2 in interactions[c1]
