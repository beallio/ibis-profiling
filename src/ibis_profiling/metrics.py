from typing import Callable
import ibis.expr.datatypes as dt
import ibis.expr.types as ir


class MetricCategory:
    COLUMN = "COLUMN"
    DISTRIBUTION = "DISTRIBUTION"
    DATASET = "DATASET"


class Metric:
    def __init__(
        self,
        name: str,
        category: str,
        applies_to: list[type[dt.DataType]] | None,
        build_expr: Callable[[ir.Column], ir.Value],
    ):
        self.name = name
        self.category = category
        self.applies_to = applies_to
        self.build_expr = build_expr

    def supports(self, column_type: dt.DataType) -> bool:
        if self.applies_to is None:
            return True
        return any(isinstance(column_type, t) for t in self.applies_to)


class MetricRegistry:
    def __init__(self):
        self.metrics: dict[str, Metric] = {}

    def register(self, metric: Metric):
        self.metrics[metric.name] = metric


registry = MetricRegistry()

# Standard Column Metrics Registration
registry.register(Metric("mean", MetricCategory.COLUMN, [dt.Numeric], lambda col: col.mean()))
registry.register(
    Metric("min", MetricCategory.COLUMN, [dt.Numeric, dt.Temporal], lambda col: col.min())
)
registry.register(
    Metric("max", MetricCategory.COLUMN, [dt.Numeric, dt.Temporal], lambda col: col.max())
)
registry.register(Metric("std", MetricCategory.COLUMN, [dt.Numeric], lambda col: col.std()))
registry.register(Metric("missing", MetricCategory.COLUMN, None, lambda col: col.isnull().sum()))
registry.register(Metric("unique", MetricCategory.COLUMN, None, lambda col: col.nunique()))
registry.register(
    Metric("zeros", MetricCategory.COLUMN, [dt.Numeric], lambda col: (col == 0).sum())
)
