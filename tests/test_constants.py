from ibis_profiling.constants import NUMERIC_ONLY_METRICS


def test_numeric_only_metrics_content():
    # Verify core metrics are present
    expected = ["mean", "std", "range", "iqr", "50%", "cv", "p_zeros"]
    for metric in expected:
        assert metric in NUMERIC_ONLY_METRICS

    # Verify no duplicates
    assert len(NUMERIC_ONLY_METRICS) == len(set(NUMERIC_ONLY_METRICS))


def test_numeric_only_metrics_is_list():
    assert isinstance(NUMERIC_ONLY_METRICS, list)
    assert len(NUMERIC_ONLY_METRICS) > 0
