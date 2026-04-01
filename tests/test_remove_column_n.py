import ibis
import pandas as pd
import polars as pl
from ibis_profiling.planner import QueryPlanner
from ibis_profiling.metrics import registry
from ibis_profiling import ProfileReport


def test_no_column_n_in_planner():
    df = pd.DataFrame({"a": [1, 2, None], "b": [4, 5, 6]})
    table = ibis.memtable(df)
    planner = QueryPlanner(table, registry)

    plans = planner.build_global_aggregation()
    assert len(plans) > 0

    # Execute the first plan and check columns
    res = plans[0].execute()
    # Convert to polars for easier column checking if it's not already
    if not isinstance(res, pl.DataFrame):
        res = pl.from_pandas(res)

    for col in res.columns:
        assert not col.endswith("__n"), f"Found redundant column count: {col}"

    assert "_dataset__row_count" in res.columns


def test_report_counts_remain_correct():
    df = pd.DataFrame({"a": [1, 2, None], "b": [4, 5, 6]})
    table = ibis.memtable(df)

    # We can use ProfileReport directly as it uses the planner
    report = ProfileReport(table)
    data = report.to_dict()

    # Check column 'a': 3 total rows, 1 missing
    stats_a = data["variables"]["a"]
    assert stats_a["n"] == 3
    assert stats_a["n_missing"] == 1
    assert stats_a["count"] == 2  # Non-null count

    # Check column 'b': 3 total rows, 0 missing
    stats_b = data["variables"]["b"]
    assert stats_b["n"] == 3
    assert stats_b["n_missing"] == 0
    assert stats_b["count"] == 3

    # Check table summary
    assert data["table"]["n"] == 3


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
