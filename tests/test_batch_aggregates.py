import ibis
import numpy as np
import pandas as pd
import pytest
import logging
from ibis_profiling import ProfileReport


def test_batch_aggregates_consistency():
    # Create a moderately wide table
    num_cols = 100
    df = pd.DataFrame({f"col_{i}": np.random.rand(10) for i in range(num_cols)})
    con = ibis.duckdb.connect()
    table = con.create_table("wide_test", df, temp=True)

    # 1. Profile with large batch size (single batch)
    report_unbatched = ProfileReport(table, global_batch_size=5000).to_dict()

    # 2. Profile with small batch size (multiple batches)
    # 100 cols * approx 10 metrics/col = 1000 expressions. Batch size 100 should trigger ~10 batches.
    report_batched = ProfileReport(table, global_batch_size=100).to_dict()

    # Verify results are identical for variables
    for col in df.columns:
        unbatched_stats = report_unbatched["variables"][col]
        batched_stats = report_batched["variables"][col]

        # Check a few key metrics
        for metric in ["mean", "min", "max", "n"]:
            assert unbatched_stats[metric] == pytest.approx(batched_stats[metric]), (
                f"Metric {metric} mismatch for {col}"
            )

    # Verify table-level stats
    assert report_unbatched["table"]["n"] == report_batched["table"]["n"]
    assert report_unbatched["table"]["n_var"] == report_batched["table"]["n_var"]


def test_batch_aggregates_warning(caplog):
    # Create a small table but set a very small batch size to trigger warning
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    con = ibis.duckdb.connect()
    table = con.create_table("warning_test", df, temp=True)

    # Each column has multiple metrics, so batch_size=2 should definitely trigger batching
    with caplog.at_level(logging.WARNING):
        ProfileReport(table, global_batch_size=2).to_dict()

    assert "Splitting global aggregates into" in caplog.text
    assert "batches to improve reliability" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__])
