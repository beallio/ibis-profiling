import ibis
import pandas as pd
import numpy as np
from ibis_profiling import Profiler


def test_n_unique_threshold_skip():
    # 100 rows, all unique
    n = 100
    df = pd.DataFrame({"high_card": np.arange(n), "low_card": [1] * n})
    table = ibis.memtable(df)

    # Set threshold to 50. Both n and n_distinct are 100 (> 50) for high_card.
    # low_card has n=100 (> 50) but n_distinct=1 (< 50), so it should NOT be skipped.
    profiler = Profiler(
        table,
        n_unique_threshold=50,
        correlations=False,
        monotonicity=False,
        compute_duplicates=False,
    )
    report = profiler.run()

    # Check high_card
    stats_high = report.variables["high_card"]
    assert stats_high["n_unique"] == "Skipped"
    assert any("Metric 'n_unique' skipped" in w for w in stats_high.get("warnings", []))

    # Check low_card
    stats_low = report.variables["low_card"]
    assert stats_low["n_unique"] == 0  # No singletons in [1, 1, ..., 1]
    assert not any("Metric 'n_unique' skipped" in w for w in stats_low.get("warnings", []))


def test_n_unique_no_threshold():
    # 100 rows, all unique
    n = 100
    df = pd.DataFrame({"high_card": np.arange(n)})
    table = ibis.memtable(df)

    # Set threshold to 0 (disabled)
    profiler = Profiler(
        table,
        n_unique_threshold=0,
        correlations=False,
        monotonicity=False,
        compute_duplicates=False,
    )
    report = profiler.run()

    # Check high_card
    stats_high = report.variables["high_card"]
    assert stats_high["n_unique"] == 100
    assert "warnings" not in stats_high or not any(
        "Metric 'n_unique' skipped" in w for w in stats_high.get("warnings", [])
    )
