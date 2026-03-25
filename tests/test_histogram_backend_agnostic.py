import ibis
import pandas as pd
import unittest.mock as mock
from ibis_profiling import ProfileReport, Profiler


def test_histogram_duckdb_backend():
    """Verify histograms work on DuckDB (default for memtable)"""
    df = pd.DataFrame(
        {"a": [1, 2, 3, 4, 5, 1, 2, 1], "b": [1.1, 2.2, 3.3, 4.4, 5.5, 1.1, 2.2, 1.1]}
    )
    table = ibis.memtable(df)

    report = ProfileReport(table)
    data = report.to_dict()

    assert "histogram" in data["variables"]["a"]
    assert "histogram" in data["variables"]["b"]


def test_histogram_dict_processing_logic():
    """
    Verify the logic for processing histogram dict results.
    We test the internal implementation by calling _run_advanced_pass
    with mocked results.
    """
    df = pd.DataFrame({"a": [1, 2, 3]})
    table = ibis.memtable(df)

    profiler = Profiler(table)
    # Mocking InternalProfileReport
    from ibis_profiling.report.report import ProfileReport as InternalProfileReport

    report = mock.MagicMock(spec=InternalProfileReport)
    report.variables = {"a": {"type": "Numeric", "min": 1, "max": 3, "mean": 2, "std": 1}}
    report.analysis = {}

    # We want to mock run_hist to return our specific dict
    mock_dict = {"bin_idx": [0, 1, 2], "count": [10, 20, 30]}

    # We patch as_completed to return our mock result
    with mock.patch("ibis_profiling.as_completed") as mock_as_completed:
        mock_future = mock.MagicMock()
        mock_future.result.return_value = ("a", mock_dict, 1.0, 3.0, 20, None)
        mock_as_completed.return_value = [mock_future]

        # We need to ensure histogram_plans is populated and parallel is True
        profiler.executor = mock.MagicMock()
        profiler.parallel = True

        profiler._run_advanced_pass(report)

        # Verify add_metric was called with our processed counts
        # It's called for metrics first, then histograms.
        # We look for the numeric_histogram call.
        found = False
        for call in report.add_metric.call_args_list:
            args = call.args
            if args[0] == "a" and args[1] == "numeric_histogram":
                found = True
                hist_data = args[2]
                assert hist_data["counts"][0] == 10
                assert hist_data["counts"][1] == 20
                assert hist_data["counts"][2] == 30
        assert found, "numeric_histogram metric not added"


if __name__ == "__main__":
    test_histogram_duckdb_backend()
    test_histogram_dict_processing_logic()
