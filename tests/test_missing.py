from ibis_profiling.report.model.missing import MissingEngine


def test_missing_logic():
    assert "bar" in MissingEngine.process({})
