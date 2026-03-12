import os
import ibis
import pytest
from ibis_profiling import ProfileReport


@pytest.mark.skip(reason="Slow performance test, run manually")
def test_profile_5M_20cols():
    data_path = "/tmp/ibis-profiling/financial_5M_20cols.parquet"
    if not os.path.exists(data_path):
        pytest.skip("Data file not found. Run scripts/profile_5M_20cols.py first.")

    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    # Test minimal
    report_min = ProfileReport(table, minimal=True)
    html_min = report_min.to_html()
    assert len(html_min) > 0
    assert "REPORT_DATA" in html_min

    # Test full (which now includes interactions)
    report_full = ProfileReport(table, minimal=False)
    html_full = report_full.to_html()
    assert len(html_full) > 0
    assert "interactions" in report_full.to_dict()
