import ibis
import pandas as pd
from ibis_profiling import Profiler


def test_leak_range_iqr():
    # Create a table with an integer column that has low cardinality
    df = pd.DataFrame({"low_card_int": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]})
    table = ibis.memtable(df)

    profiler = Profiler(table, cardinality_threshold=5)
    report = profiler.run()

    # Check low_card_int
    stats = report.variables["low_card_int"]
    print(f"Stats keys: {list(stats.keys())}")

    assert stats["type"] == "Categorical"

    # These SHOULD NOT be there
    leaked_metrics = ["range", "iqr"]
    for metric in leaked_metrics:
        if metric in stats:
            print(f"FAILURE: Metric {metric} leaked into Categorical column!")
        else:
            print(f"SUCCESS: Metric {metric} was not found.")


if __name__ == "__main__":
    test_leak_range_iqr()
