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


def safe_col(col: ir.Column, for_stats: bool = False) -> ir.Column:
    """Treats NaNs as NULLs and optionally casts to Float64 for statistical operations."""
    dtype = col.type()

    # Only cast to Float64 if specifically requested for stats (mean, std, etc.)
    # to avoid precision loss on large integers.
    if for_stats and isinstance(dtype, dt.Numeric):
        col = col.cast(dt.Float64)

    if isinstance(dtype, (dt.Float64, dt.Float32)):
        return col.isnan().cases((True, None), else_=col)
    return col


# Standard Column Metrics Registration
registry.register(
    Metric(
        "mean",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).mean(),
    )
)
registry.register(
    Metric("min", MetricCategory.COLUMN, [dt.Numeric, dt.Temporal], lambda col: safe_col(col).min())
)
registry.register(
    Metric("max", MetricCategory.COLUMN, [dt.Numeric, dt.Temporal], lambda col: safe_col(col).max())
)
registry.register(
    Metric(
        "std",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).std(how="sample"),
    )
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
    value_col = vc.columns[0]
    count_col = vc.columns[1]
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
    Metric(
        "median",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).median(),
    )
)
registry.register(
    Metric(
        "p5",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).quantile(0.05),
    )
)
registry.register(
    Metric(
        "p25",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).quantile(0.25),
    )
)
registry.register(
    Metric(
        "p75",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).quantile(0.75),
    )
)
registry.register(
    Metric(
        "p95",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).quantile(0.95),
    )
)
registry.register(
    Metric(
        "variance",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).var(),
    )
)
# registry.register(Metric("skewness", ...))

registry.register(
    Metric(
        "kurtosis",
        MetricCategory.COLUMN,
        [dt.Numeric],
        lambda col: safe_col(col, for_stats=True).kurtosis(),
    )
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
registry.register(
    Metric("n_empty", MetricCategory.COLUMN, [dt.String], lambda col: (col == "").sum())
)
