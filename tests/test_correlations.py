from ibis_profiling.report.model.correlations import CorrelationEngine


def test_correlations_logic():
    assert CorrelationEngine.compute_pearson(None, []) == {}
