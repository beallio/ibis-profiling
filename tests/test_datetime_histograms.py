import ibis
import polars as pl
from datetime import datetime, date
from ibis_profiling import ProfileReport


def test_datetime_histogram_with_objects():
    """Verify that DateTime histograms are generated when min/max are datetime objects."""
    data = {
        "dt": [
            datetime(2023, 1, 1),
            datetime(2023, 1, 2),
            datetime(2023, 1, 3),
            datetime(2023, 1, 4),
        ],
    }
    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    # In current state, this might still work if they are converted to strings in _build
    # We want to ensure that _run_advanced_pass handles them if they are objects.

    # We can mock the stats to ensure they ARE objects when _run_advanced_pass sees them
    report = ProfileReport(table)

    # Check if histogram exists currently
    # Based on the review, it might be failing silently
    stats = report.get_description()["variables"]["dt"]

    # If it's already failing, 'histogram' will be missing
    assert "histogram" in stats, "Histogram should be present for DateTime column"
    assert len(stats["histogram"]["bins"]) > 0


def test_date_histogram_with_objects():
    """Verify that Date (not datetime) histograms are generated when min/max are date objects."""
    data = {
        "d": [
            date(2023, 1, 1),
            date(2023, 1, 2),
            date(2023, 1, 3),
            date(2023, 1, 4),
        ],
    }
    df = pl.DataFrame(data)
    table = ibis.memtable(df)

    report = ProfileReport(table)
    stats = report.get_description()["variables"]["d"]

    assert "histogram" in stats, "Histogram should be present for Date column"
