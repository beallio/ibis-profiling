import ibis
import polars as pl
from datetime import datetime, date
import unittest.mock as mock
from ibis_profiling import Profiler, InternalProfileReport


def test_isoparse_not_called_for_objects():
    """Verify that dateutil.parser.isoparse is not called for datetime objects."""
    data = {"dt": [datetime(2023, 1, 1), datetime(2023, 1, 2)]}
    table = ibis.memtable(data)

    # We'll use a manually constructed report to bypass serialization strings
    raw_results = pl.DataFrame(
        {
            "dt__min": [datetime(2023, 1, 1)],
            "dt__max": [datetime(2023, 1, 2)],
            "_dataset__row_count": [2],
        }
    )
    schema = {"dt": "DateTime"}
    report = InternalProfileReport(raw_results, schema)

    # Inject objects back into the report manually because _build() might have serialized them
    report.variables["dt"]["min"] = datetime(2023, 1, 1)
    report.variables["dt"]["max"] = datetime(2023, 1, 2)
    report.variables["dt"]["type"] = "DateTime"

    profiler = Profiler(table)

    with mock.patch("dateutil.parser.isoparse") as mock_isoparse:
        profiler._run_advanced_pass(report)

        # isoparse should NOT be called because they are objects
        assert not mock_isoparse.called

    assert "histogram" in report.variables["dt"]


def test_warning_for_failed_conversion():
    """Verify that a warning is added if min/max conversion fails."""
    data = {"dt": [datetime(2023, 1, 1), datetime(2023, 1, 2)]}
    table = ibis.memtable(data)

    raw_results = pl.DataFrame(
        {
            "dt__min": [datetime(2023, 1, 1)],
            "dt__max": [datetime(2023, 1, 2)],
            "_dataset__row_count": [2],
        }
    )
    schema = {"dt": "DateTime"}
    report = InternalProfileReport(raw_results, schema)

    # Inject something that to_timestamp() can't handle (neither string nor timestampable)
    report.variables["dt"]["min"] = complex(1, 1)  # Un-convertible object
    report.variables["dt"]["max"] = complex(2, 2)
    report.variables["dt"]["type"] = "DateTime"

    profiler = Profiler(table)
    profiler._run_advanced_pass(report)

    # Check for warning
    assert "warnings" in report.analysis
    assert any("Could not convert min/max" in w for w in report.analysis["warnings"])

    # Histogram should be missing because conversion failed
    assert "histogram" not in report.variables["dt"]


def test_date_object_handling():
    """Verify that date objects are correctly handled."""

    data = {"d": [date(2023, 1, 1), date(2023, 1, 2)]}
    table = ibis.memtable(data)

    raw_results = pl.DataFrame(
        {"d__min": [date(2023, 1, 1)], "d__max": [date(2023, 1, 2)], "_dataset__row_count": [2]}
    )
    schema = {"d": "DateTime"}
    report = InternalProfileReport(raw_results, schema)

    # Inject date objects
    report.variables["d"]["min"] = date(2023, 1, 1)
    report.variables["d"]["max"] = date(2023, 1, 2)
    report.variables["d"]["type"] = "DateTime"

    profiler = Profiler(table)
    profiler._run_advanced_pass(report)

    assert "histogram" in report.variables["d"]
    assert report.variables["d"]["histogram"]["bins"] != []
