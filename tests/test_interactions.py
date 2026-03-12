import ibis
from ibis_profiling import profile


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
