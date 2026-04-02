import ibis
import pandas as pd
from ibis_profiling import ProfileReport


def test_empty_string_tracking():
    # Dataset with mixture of NULLs, Empty Strings, and valid data
    df = pd.DataFrame(
        {
            "mixed": ["a", "", None, "b", "", ""],  # 6 rows: 1 null, 3 empty, 2 valid
            "all_empty": ["", "", "", "", "", ""],  # 6 rows: 6 empty
            "no_empty": ["a", "b", "c", "d", "e", "f"],  # 6 rows: 0 empty
        }
    )
    table = ibis.memtable(df)
    report = ProfileReport(table)
    data = report.to_dict()

    # Verify 'mixed' column
    mixed = data["variables"]["mixed"]
    assert mixed["n_empty"] == 3
    assert mixed["n_missing"] == 1
    assert mixed.get("p_empty") is not None
    assert mixed["p_empty"] == 0.5
    assert mixed["p_missing"] == 1 / 6

    # Verify semantic labeling in histogram
    histogram = mixed["histogram"]
    assert "(Empty)" in histogram["bins"]
    empty_idx = histogram["bins"].index("(Empty)")
    assert histogram["counts"][empty_idx] == 3

    # Verify 'all_empty' column
    all_empty = data["variables"]["all_empty"]
    assert all_empty["n_empty"] == 6
    assert all_empty["p_empty"] == 1.0

    # Verify alerts
    alerts = data["alerts"]
    # Check for EMPTY alert on 'mixed' and 'all_empty'
    empty_alerts = [a for a in alerts if a["alert_type"] == "EMPTY"]
    assert len(empty_alerts) == 1
    assert "mixed" in empty_alerts[0]["fields"]
    assert "all_empty" in empty_alerts[0]["fields"]

    # 'all_empty' should also have a CONSTANT alert
    constant_alerts = [a for a in alerts if a["alert_type"] == "CONSTANT"]
    assert any("all_empty" in a["fields"] for a in constant_alerts)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
