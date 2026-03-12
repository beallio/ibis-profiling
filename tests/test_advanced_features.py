import ibis
from ibis_profiling import ProfileReport


def test_extreme_values():
    schema = ibis.schema({"a": "int64"})
    # 1 to 10
    data = [{"a": i} for i in range(1, 11)]
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=False)  # Full mode
    stats = report.get_description()["variables"]["a"]

    assert "extreme_values_smallest" in stats
    assert "extreme_values_largest" in stats
    assert stats["extreme_values_smallest"] == [1, 2, 3, 4, 5]
    assert stats["extreme_values_largest"] == [10, 9, 8, 7, 6]


def test_monotonicity():
    schema = ibis.schema({"inc": "int64", "dec": "int64", "none": "int64"})
    data = [
        {"inc": 1, "dec": 10, "none": 5},
        {"inc": 2, "dec": 9, "none": 1},
        {"inc": 3, "dec": 8, "none": 10},
    ]
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=False)
    vars = report.get_description()["variables"]

    assert vars["inc"]["monotonic_increasing"] is True
    assert vars["inc"]["monotonic_decreasing"] is False

    assert vars["dec"]["monotonic_increasing"] is False
    assert vars["dec"]["monotonic_decreasing"] is True

    assert vars["none"]["monotonic_increasing"] is False
    assert vars["none"]["monotonic_decreasing"] is False


def test_string_length_metrics():
    schema = ibis.schema({"s": "string"})
    data = [{"s": "a"}, {"s": "abc"}, {"s": ""}]  # Lengths: 1, 3, 0
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=False)
    stats = report.get_description()["variables"]["s"]

    assert stats["min_length"] == 0
    assert stats["max_length"] == 3
    assert stats["mean_length"] == 4 / 3
    assert "length_histogram" in stats
    # bins are labels, so "0", "1", "3"
    assert "0" in stats["length_histogram"]["bins"]
    assert "1" in stats["length_histogram"]["bins"]
    assert "3" in stats["length_histogram"]["bins"]


def test_spearman_correlation():
    schema = ibis.schema({"a": "float64", "b": "float64"})
    # Perfect monotonic but non-linear: b = exp(a)
    import math

    data = [{"a": float(i), "b": math.exp(i)} for i in range(1, 6)]
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=False)
    corrs = report.get_description()["correlations"]

    assert "spearman" in corrs
    # Perfect correlation should be 1.0 (or very close)
    # Spearman should be 1.0 because it's perfectly monotonic
    # Format is now list of dicts
    assert corrs["spearman"][0]["b"] > 0.99
