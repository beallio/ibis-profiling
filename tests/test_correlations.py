from ibis_profiling.report.model.correlations import CorrelationEngine


def test_correlations_logic():
    assert CorrelationEngine._compute_pearson(None, []) == {"columns": [], "matrix": []}
