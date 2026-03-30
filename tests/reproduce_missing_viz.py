import ibis
import pandas as pd
from ibis_profiling import Profiler


def test_missing_viz_logic():
    # Dataset with missing values in 2 columns
    df = pd.DataFrame(
        {"a": [1, 2, None, 4, 5], "b": [None, 2, 3, 4, 5], "cat_high": [str(i) for i in range(5)]}
    )
    table = ibis.memtable(df)

    # We set a low threshold to test skip logic too
    profiler = Profiler(table, n_unique_threshold=10)
    report = profiler.run()

    # 1. Check cat_high histogram (should exist because 5 < 10)
    stats = report.variables["cat_high"]
    assert "histogram" in stats, "Histogram missing for high cardinality column under threshold"

    # 2. Check Missingness Heatmap (should exist because 2 columns have missing)
    assert report.missing is not None
    assert "heatmap" in report.missing
    assert len(report.missing["heatmap"]["matrix"]["columns"]) == 2


if __name__ == "__main__":
    test_missing_viz_logic()
    print("Test passed!")
