import ibis
import pandas as pd
import numpy as np
from ibis_profiling import ProfileReport


def test_report_components_presence():
    # Create data that should trigger alerts and missingness components
    df = pd.DataFrame(
        {
            "constant": [1] * 100,
            "mostly_null": [1 if i % 10 == 0 else None for i in range(100)],
            "all_unique": np.arange(100),
        }
    )
    table = ibis.memtable(df)
    report = ProfileReport(table)

    # Get the dictionary representation
    report_dict = report.to_dict()

    # 1. Verify Overview stats (Table Summary)
    table_stats = report_dict.get("table", {})
    print(f"Table stats: {table_stats}")
    assert table_stats.get("n") == 100
    assert table_stats.get("n_var") == 3
    # n_vars_constant should be at least 1 (for 'constant' column)
    assert table_stats.get("n_vars_constant", 0) >= 1
    # n_cells_missing should be 90 (from 'mostly_null' column)
    n_cells = table_stats.get("n_cells_missing")
    print(f"n_cells_missing: {n_cells}")

    mostly_null_stats = report_dict["variables"]["mostly_null"]
    print(f"mostly_null stats: {mostly_null_stats}")

    assert n_cells == 90

    # 2. Verify Alerts
    alerts = report_dict.get("alerts", [])
    alert_types = [a["alert_type"] for a in alerts]
    print(f"Alerts found: {alert_types}")
    assert len(alerts) > 0, "No alerts generated"
    assert "CONSTANT" in alert_types, f"CONSTANT alert missing. Types: {alert_types}"
    assert "UNIQUE" in alert_types, f"UNIQUE alert missing. Types: {alert_types}"
    assert "MISSING" in alert_types, f"MISSING alert missing. Types: {alert_types}"

    # 3. Verify Missingness Matrix
    missing = report_dict.get("missing", {})
    print(f"Missing keys: {list(missing.keys())}")

    matrix_section = missing.get("matrix", {}).get("matrix", {})
    print(f"Matrix section keys: {list(matrix_section.keys())}")
    assert "columns" in matrix_section
    assert "matrix" in matrix_section

    # The matrix should be a list of dicts (after _format_matrices processing)
    rows = matrix_section["matrix"]
    print(f"First matrix row type: {type(rows[0]) if rows else 'N/A'}")
    assert len(rows) == 100
    assert isinstance(rows[0], dict), f"Expected list of dicts, got list of {type(rows[0])}"
    assert "mostly_null" in rows[0]


if __name__ == "__main__":
    test_report_components_presence()
    print("Test passed!")
