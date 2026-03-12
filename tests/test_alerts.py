from ibis_profiling.report.model.alerts import AlertEngine


def test_alerts_logic():
    assert AlertEngine.get_alerts({}, {}) == []
