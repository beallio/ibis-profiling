import ibis
import pandas as pd
from ibis_profiling import Profiler


def test_p_unique_is_calculated():
    # 10 rows, 5 unique (singletons), 5 non-unique (duplicates)
    # data: [1, 2, 3, 4, 5, 6, 6, 7, 7, 8]
    # singletons: 1, 2, 3, 4, 5, 8 (n_unique = 6)
    # distinct: 1, 2, 3, 4, 5, 6, 7, 8 (n_distinct = 8)
    df = pd.DataFrame({"col": [1, 2, 3, 4, 5, 6, 6, 7, 7, 8]})
    table = ibis.memtable(df)

    profiler = Profiler(table, correlations=False, monotonicity=False, compute_duplicates=False)
    report = profiler.run()

    stats = report.variables["col"]
    assert stats["n_unique"] == 6
    assert stats["n_distinct"] == 8

    # p_unique should be 6/10 = 0.6
    # Before the fix, it would be 0.0 because it was calculated in _build()
    assert stats["p_unique"] == 0.6
    assert stats["p_distinct"] == 0.8


def test_top_values_threshold():
    # Verify that top_values is also skipped above threshold
    n = 100
    df = pd.DataFrame({"high_card": [str(i) for i in range(n)]})
    table = ibis.memtable(df)

    # Set threshold to 50
    profiler = Profiler(
        table,
        n_unique_threshold=50,
        correlations=False,
        monotonicity=False,
        compute_duplicates=False,
    )
    report = profiler.run()

    stats = report.variables["high_card"]
    # Check that top_values was skipped
    assert stats["top_values"] == "Skipped"
    assert any("Frequency table skipped" in w for w in stats.get("warnings", []))
