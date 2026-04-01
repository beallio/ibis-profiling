import polars as pl
from unittest import mock
from ibis_profiling.report.report import ProfileReport


def test_finalize_idempotency():
    raw_results = pl.DataFrame(
        {"_dataset__row_count": [10], "a__n_missing": [2], "a__n_distinct": [5]}
    )
    schema = {"a": pl.Int64}
    report = ProfileReport(raw_results, schema)

    # Mock AlertEngine.get_alerts to count calls
    with mock.patch("ibis_profiling.report.report.AlertEngine.get_alerts") as mock_alerts:
        mock_alerts.return_value = []

        # First call
        report.finalize()
        assert mock_alerts.call_count == 1
        assert report._finalized is True

        # Second call
        report.finalize()
        assert mock_alerts.call_count == 1  # Should not have increased

        # Third call via to_dict
        report.to_dict()
        assert mock_alerts.call_count == 1  # Should still be 1


def test_serialization_no_mutation():
    raw_results = pl.DataFrame(
        {"_dataset__row_count": [10], "a__n_missing": [2], "a__n_distinct": [5]}
    )
    schema = {"a": pl.Int64}
    report = ProfileReport(raw_results, schema)

    # First serialization
    dict1 = report.to_dict()

    # Second serialization
    dict2 = report.to_dict()

    # Ensure they are identical
    assert dict1 == dict2

    # Third serialization (JSON)
    json1 = report.to_json()
    json2 = report.to_json()
    assert json1 == json2


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
