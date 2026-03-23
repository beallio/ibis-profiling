import os
import polars as pl
from ibis_profiling import ProfileReport


def test_from_excel_kwargs_routing():
    """Test that profiling kwargs don't leak into polars.read_excel."""
    os.makedirs("/tmp/ibis-profiling", exist_ok=True)
    file_path = "/tmp/ibis-profiling/test_from_excel.xlsx"
    df = pl.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
    df.write_excel(file_path)

    try:
        # Pass profiling-specific kwargs like correlations=False, compute_duplicates=False
        # If kwargs are misrouted, pl.read_excel will throw a TypeError.
        report = ProfileReport.from_excel(
            file_path, correlations=False, compute_duplicates=False, title="Test Excel Report"
        )
        assert report is not None
        # Check removed
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
