import ibis.expr.datatypes as dt
from ibis_profiling.metrics import registry, Metric, MetricCategory


def test_metric_supports():
    metric = Metric("mean", MetricCategory.COLUMN, [dt.Numeric], lambda col: col.mean())

    assert metric.supports(dt.Int64())
    assert metric.supports(dt.Float64())
    assert not metric.supports(dt.String())


def test_registry_registration():
    m = Metric("test", MetricCategory.COLUMN, None, lambda col: col.count())
    registry.register(m)

    assert "test" in registry.metrics
    assert registry.metrics["test"] == m
