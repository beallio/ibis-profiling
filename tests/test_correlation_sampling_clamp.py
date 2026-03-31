import ibis
import pandas as pd
import pytest
from ibis_profiling.report.model.correlations import CorrelationEngine


def test_correlation_sampling_fraction_clamp():
    # 20 rows
    df = pd.DataFrame({"a": range(20), "b": range(20, 40)})
    con = ibis.duckdb.connect()
    table = con.create_table("test_table", df)

    # row_count (20) > sampling_threshold (10) -> is_sampled = True
    # sample_size (100) / row_count (20) = 5.0 -> Error in sample()

    try:
        # We pass row_count=20 explicitly to avoid count() query for speed
        results = CorrelationEngine.compute_all(
            table, variables={}, row_count=20, sampling_threshold=10, sample_size=100
        )
        # Even though row_count > sampling_threshold,
        # since sample_size >= row_count, we shouldn't actually sample.
        assert results["pearson"]["sampled"] is False
    except Exception as e:
        # If it fails with 'sampling fraction must be between 0 and 1' or similar
        pytest.fail(f"CorrelationEngine.compute_all failed with sampling fraction > 1.0: {e}")
    finally:
        con.disconnect()


def test_correlation_sampling_normal():
    # 100 rows
    df = pd.DataFrame({"a": range(100), "b": range(100, 200)})
    con = ibis.duckdb.connect()
    table = con.create_table("test_table_normal", df)

    # row_count (100) > sampling_threshold (10) -> is_sampled = True
    # sample_size (50) / row_count (100) = 0.5 -> Should sample

    results = CorrelationEngine.compute_all(
        table, variables={}, row_count=100, sampling_threshold=10, sample_size=50
    )
    assert results["pearson"]["sampled"] is True
    con.disconnect()


if __name__ == "__main__":
    test_correlation_sampling_fraction_clamp()
    test_correlation_sampling_normal()
