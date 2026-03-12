import ibis
import polars as pl
from ibis_profiling import profile


def test_two_pass_skewness():
    # Setup data with known skewness
    # Data: [1, 1, 1, 1, 10]
    # Mean: 2.8, Std: 4.02
    data = {"val": [1.0, 1.0, 1.0, 1.0, 10.0]}
    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    report = profile(table)
    result = report.to_dict()

    # Skewness should be computed in the 2nd pass
    val_stats = result["variables"]["val"]
    assert "skewness" in val_stats
    assert val_stats["skewness"] > 0  # Right skewed


def test_all_types_histogram():
    data = {
        "num": [1, 2, 3, 4, 5],
        "cat": ["a", "b", "a", "b", "c"],
        "bool": [True, False, True, False, True],
    }
    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    report = profile(table)
    result = report.to_dict()

    for col in ["num", "cat", "bool"]:
        assert "histogram" in result["variables"][col]
        assert len(result["variables"][col]["histogram"]["bins"]) > 0
