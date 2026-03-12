from ibis_profiling.report.model.alerts import AlertEngine


def test_alert_detection():
    # Setup data that should trigger all major alerts
    # n=100
    # col1: all "A" -> CONSTANT
    # col2: 1..100 -> UNIQUE
    # col3: 90% nulls -> MISSING
    # col4: 90% zeros -> ZEROS
    # col5: UUID strings (Categorical) -> HIGH_CARDINALITY

    table_stats = {"n": 100}
    variables = {
        "constant": {"n_distinct": 1, "p_missing": 0.0, "type": "Categorical"},
        "unique": {"n_distinct": 100, "p_missing": 0.0, "type": "Numeric"},
        "missing": {"n_distinct": 10, "p_missing": 0.9, "type": "Numeric"},
        "zeros": {"n_distinct": 2, "p_missing": 0.0, "n_zeros": 90, "type": "Numeric"},
        "high_card": {"n_distinct": 80, "p_missing": 0.0, "type": "Categorical"},
    }

    alerts = AlertEngine.get_alerts(table_stats, variables)
    alert_types = [a["alert_type"] for a in alerts]

    assert "CONSTANT" in alert_types
    assert "UNIQUE" in alert_types
    assert "MISSING" in alert_types
    assert "ZEROS" in alert_types
    assert "HIGH_CARDINALITY" in alert_types

    # Specific check for fields
    constant_alert = [a for a in alerts if a["alert_type"] == "CONSTANT"][0]
    assert constant_alert["fields"] == ["constant"]
