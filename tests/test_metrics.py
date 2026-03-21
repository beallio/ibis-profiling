import ibis
import pandas as pd
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


def test_n_unique_metric_robustness():
    """Verify that n_unique metric works with dynamic column naming from value_counts()."""
    df = pd.DataFrame({"col_A": [1, 2, 2, 3], "col_B": ["a", "b", "c", "c"]})
    table = ibis.memtable(df)

    n_unique_metric = registry.metrics["n_unique"]

    # Check col_A: 1 and 3 are unique (singletons). n_unique should be 2.
    expr_A = n_unique_metric.build_expr(table.col_A)
    # Check col_B: 'a' and 'b' are unique (singletons). n_unique should be 2.
    expr_B = n_unique_metric.build_expr(table.col_B)

    # We execute using DuckDB (default for memtable)
    assert expr_A.to_pyarrow().as_py() == 2
    assert expr_B.to_pyarrow().as_py() == 2
