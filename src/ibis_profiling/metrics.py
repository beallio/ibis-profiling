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


def safe_col(col: ir.Column) -> ir.Column:
    """Treats NaNs as NULLs and casts Numeric types to Float64 for statistical stability."""
    # Cast to Float64 first to avoid overflow in intermediate calculations
    # and to ensure consistent behavior across backends for stats functions.
    if isinstance(col.type(), dt.Numeric):
        col = col.cast(dt.Float64)

    if isinstance(col.type(), (dt.Float64, dt.Float32)):
        return col.isnan().cases((True, None), else_=col)
    return col


# Standard Column Metrics Registration
registry.register(
    Metric("mean", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).mean())
)
registry.register(
    Metric("min", MetricCategory.COLUMN, [dt.Numeric, dt.Temporal], lambda col: safe_col(col).min())
)
registry.register(
    Metric("max", MetricCategory.COLUMN, [dt.Numeric, dt.Temporal], lambda col: safe_col(col).max())
)
registry.register(
    Metric("std", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).std(how="sample"))
)
registry.register(
    Metric("missing", MetricCategory.COLUMN, None, lambda col: safe_col(col).isnull().sum())
)
registry.register(
    Metric("n_distinct", MetricCategory.COLUMN, None, lambda col: safe_col(col).nunique())
)
registry.register(
    Metric("zeros", MetricCategory.COLUMN, [dt.Numeric], lambda col: (col == 0).sum())
)
registry.register(
    Metric("n_negative", MetricCategory.COLUMN, [dt.Numeric], lambda col: (col < 0).sum())
)


# n_unique (singletons) is added as a COLUMN metric, but note it might require special handling in the planner
def _n_unique_expr(col: ir.Column) -> ir.Value:
    vc = col.value_counts()
    count_col = "count" if "count" in vc.columns else vc.columns[1]
    value_col = vc.columns[0]
    return vc.filter((vc[count_col] == 1) & vc[value_col].notnull()).count()


registry.register(Metric("n_unique", MetricCategory.COLUMN, None, _n_unique_expr))
registry.register(
    Metric(
        "infinite", MetricCategory.COLUMN, [dt.Float64, dt.Float32], lambda col: col.isinf().sum()
    )
)

registry.register(
    Metric("sum", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).sum())
)
registry.register(
    Metric("median", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).median())
)
registry.register(
    Metric("p5", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).quantile(0.05))
)
registry.register(
    Metric("p25", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).quantile(0.25))
)
registry.register(
    Metric("p75", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).quantile(0.75))
)
registry.register(
    Metric("p95", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).quantile(0.95))
)
registry.register(
    Metric("variance", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).var())
)
# registry.register(Metric("skewness", ...))

registry.register(
    Metric("kurtosis", MetricCategory.COLUMN, [dt.Numeric], lambda col: safe_col(col).kurtosis())
)

# Text Metrics
registry.register(
    Metric("mean_length", MetricCategory.COLUMN, [dt.String], lambda col: col.length().mean())
)
registry.register(
    Metric("min_length", MetricCategory.COLUMN, [dt.String], lambda col: col.length().min())
)
registry.register(
    Metric("max_length", MetricCategory.COLUMN, [dt.String], lambda col: col.length().max())
)
