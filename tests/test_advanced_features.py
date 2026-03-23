import ibis
from ibis_profiling import ProfileReport


def test_extreme_values():
    schema = ibis.schema({"val": "int64"})
    # Cardinality > 0.5 * 10 = 5 to ensure it doesn't use distinct optimization
    data = [{"val": i} for i in range(1, 11)]
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=False, cardinality_threshold=0)
    stats = report.get_description()["variables"]["val"]

    assert "extreme_values_smallest" in stats
    assert "extreme_values_largest" in stats
    assert stats["extreme_values_smallest"] == [1, 2, 3, 4, 5]
    assert stats["extreme_values_largest"] == [10, 9, 8, 7, 6]


def test_monotonicity():
    schema = ibis.schema({"inc": "float64", "dec": "float64", "none": "float64", "id": "int64"})
    data = [
        {"inc": 1.0, "dec": 10.0, "none": 5.0, "id": 1},
        {"inc": 2.0, "dec": 9.0, "none": 1.0, "id": 2},
        {"inc": 3.0, "dec": 8.0, "none": 10.0, "id": 3},
    ]
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=False, monotonicity_order_by="id")
    vars = report.get_description()["variables"]

    assert vars["inc"]["monotonic_increasing"] is True
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


def test_quantile_statistics():
    schema = ibis.schema({"val": "float64"})
    data = [{"val": i} for i in range(1, 101)]  # 1 to 100
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=False)
    stats = report.get_description()["variables"]["val"]

    # DuckDB/Ibis quantiles are approximate but should be close
    assert 4.0 <= stats["5%"] <= 6.0
    assert 24.0 <= stats["25%"] <= 26.0
    assert 49.0 <= stats["50%"] <= 51.0
    assert 74.0 <= stats["75%"] <= 76.0
    assert 94.0 <= stats["95%"] <= 96.0

    assert stats["range"] == 99.0
    assert 48.0 <= stats["iqr"] <= 52.0
    assert stats["cv"] > 0
