import json
import polars as pl
import pytest
import ibis.expr.datatypes as dt
from ibis_profiling.report import ProfileReport


def test_json_serialization_handles_complex_types():
    # Test all problematic types together
    from datetime import datetime

    raw_results = pl.DataFrame(
        [
            {
                "a__min": datetime(2023, 1, 1),
                "b__mean": 10.5,
                "_dataset__row_count": 20000000,
            }
        ]
    )
    schema = {"a": dt.Timestamp(), "b": dt.Float64()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    # This should now PASS
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Check values
    assert result["table"]["n"] == 20000000
    assert result["variables"]["a"]["min"] == "2023-01-01T00:00:00"
    assert result["variables"]["b"]["mean"] == 10.5


if __name__ == "__main__":
    pytest.main([__file__])
