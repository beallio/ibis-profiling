import ibis
import pandas as pd
import pytest
from ibis_profiling import ProfileReport


def test_invalid_sampling_parameters():
    df = pd.DataFrame({"a": range(100), "b": range(100)})
    con = ibis.duckdb.connect()
    table = con.create_table("test_table", df, temp=True)

    # 1. Test zero sample size
    report = ProfileReport(table, correlations_sample_size=0).to_dict()
    warnings = report["analysis"].get("warnings", [])
    assert any("correlations_sample_size" in w for w in warnings)

    # 2. Test negative sampling threshold
    report = ProfileReport(table, correlations_sampling_threshold=-1).to_dict()
    warnings = report["analysis"].get("warnings", [])
    assert any("correlations_sampling_threshold" in w for w in warnings)


def test_empty_table_sampling():
    # Test that row_count=0 doesn't cause division by zero
    schema = ibis.schema({"a": "int64"})
    con = ibis.duckdb.connect()
    table = con.create_table("empty_table", schema=schema, temp=True)

    # This should not crash
    report = ProfileReport(table).to_dict()
    assert report["table"]["n"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
