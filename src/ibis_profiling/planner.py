import ibis
from .metrics import MetricRegistry, MetricCategory


class QueryPlanner:
    def __init__(self, table: ibis.Table, registry: MetricRegistry):
        self.table = table
        self.registry = registry

    def build_global_aggregation(self) -> ibis.expr.types.Table:
        """Batches all applicable COLUMN metrics into a single aggregation query."""
        schema = self.table.schema()
        aggs = []

        for col_name, dtype in schema.items():
            col = self.table[col_name]
            for metric in self.registry.metrics.values():
                if metric.category == MetricCategory.COLUMN and metric.supports(dtype):
                    # We namespace the alias to reconstruct the report later
                    expr_alias = f"{col_name}__{metric.name}"
                    aggs.append(metric.build_expr(col).name(expr_alias))

        # Include dataset-wide metrics
        aggs.append(self.table.count().name("_dataset__row_count"))

        return self.table.aggregate(aggs)
