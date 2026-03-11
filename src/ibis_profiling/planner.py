import ibis
from .metrics import MetricRegistry, MetricCategory


class QueryPlanner:
    def __init__(self, table: ibis.Table, registry: MetricRegistry):
        self.table = table
        self.registry = registry

    def build_global_aggregation(self) -> ibis.expr.types.Table:
        """Batches all applicable simple COLUMN metrics into a single aggregation query."""
        schema = self.table.schema()
        aggs = []

        for col_name, dtype in schema.items():
            col = self.table[col_name]
            for metric in self.registry.metrics.values():
                # We skip n_unique for now as it's complex
                if metric.name == "n_unique":
                    continue

                if metric.category == MetricCategory.COLUMN and metric.supports(dtype):
                    # We namespace the alias to reconstruct the report later
                    expr_alias = f"{col_name}__{metric.name}"
                    aggs.append(metric.build_expr(col).name(expr_alias))

        # Include dataset-wide metrics
        aggs.append(self.table.count().name("_dataset__row_count"))

        return self.table.aggregate(aggs)

    def build_complex_metrics(self) -> list[tuple[str, str, ibis.expr.types.Value]]:
        """
        Returns a list of (column_name, metric_name, expression) for metrics
        that cannot be batched in a single pass.
        """
        schema = self.table.schema()
        plans = []

        for col_name, dtype in schema.items():
            col = self.table[col_name]
            # 1. n_unique (singletons)
            metric = self.registry.metrics.get("n_unique")
            if metric and metric.supports(dtype):
                plans.append((col_name, metric.name, metric.build_expr(col)))

            # 2. Histograms / Distribution (top values) for ALL columns
            # We treat top-values as the "distribution" for the UI.
            # For numeric columns, it acts as a frequency plot of values.
            # For categorical, it's the standard value counts.
            hist_expr = col.value_counts().order_by(ibis.desc(f"{col_name}_count")).limit(20)
            plans.append((col_name, "top_values", hist_expr))

        return plans
