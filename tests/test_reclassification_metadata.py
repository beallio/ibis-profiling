import ibis
import pandas as pd
from ibis_profiling import Profiler


def test_reclassification_metadata():
    # Create a table with an integer column that has low cardinality
    df = pd.DataFrame(
        {"low_card_int": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2], "high_card_int": list(range(10))}
    )
    table = ibis.memtable(df)

    profiler = Profiler(table, cardinality_threshold=5)
    report = profiler.run()

    # Check low_card_int
    stats = report.variables["low_card_int"]
    assert stats["type"] == "Categorical"

    # Numeric-only metrics should NOT be present
    numeric_metrics = [
        "mean",
        "std",
        "variance",
        "skewness",
        "kurtosis",
        "mad",
        "sum",
        "range",
        "iqr",
        "50%",
        "5%",
        "25%",
        "75%",
        "95%",
    ]

    for metric in numeric_metrics:
        assert metric not in stats, f"Metric {metric} should not be in categorical column metadata"

    # Check high_card_int
    stats_high = report.variables["high_card_int"]
    assert stats_high["type"] == "Numeric"
    assert "mean" in stats_high

    # Check report.table["types"]
    types = report.table.get("types", {})
    assert types.get("Numeric") == 1
    assert types.get("Categorical") == 1


if __name__ == "__main__":
    test_reclassification_metadata()
    print("Test passed!")
