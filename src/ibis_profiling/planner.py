import ibis
import ibis.expr.types as ir
import ibis.expr.datatypes as dt
from .metrics import MetricRegistry, MetricCategory


class QueryPlanner:
    def __init__(self, table: ibis.Table, registry: MetricRegistry):
        self.table = table
        self.registry = registry

    def build_global_aggregation(self) -> ir.Table:
        """Batches all applicable simple COLUMN metrics into a single aggregation query."""
        schema = self.table.schema()
        aggs = []

        for col_name, dtype in schema.items():
            col = self.table[col_name]
            for metric in self.registry.metrics.values():
                # We skip n_unique (singletons) for now as it's complex (requires value_counts)
                if metric.name == "n_unique":
                    continue

                if metric.category == MetricCategory.COLUMN and metric.supports(dtype):
                    # We namespace the alias to reconstruct the report later
                    expr_alias = f"{col_name}__{metric.name}"
                    aggs.append(metric.build_expr(col).name(expr_alias))

        # Include dataset-wide metrics
        aggs.append(self.table.count().name("_dataset__row_count"))

        # We'll omit distinct count from this global batch to avoid IntegrityErrors
        # and handle it in __init__.py as a separate pass.

        return self.table.aggregate(aggs)

    def build_singleton_batches(self, batch_size: int = 50) -> list[ir.Table]:
        """
        Batches singleton count (n_unique) calculations into multiple passes
        using window functions to avoid OOM on wide tables.
        """
        schema = self.table.schema()
        cols_to_profile = []

        metric = self.registry.metrics.get("n_unique")
        if not metric:
            return []

        for col_name, dtype in schema.items():
            if metric.supports(dtype):
                cols_to_profile.append(col_name)

        if not cols_to_profile:
            return []

        batches = []
        for i in range(0, len(cols_to_profile), batch_size):
            batch_cols = cols_to_profile[i : i + batch_size]
            mutates = {}
            for col_name in batch_cols:
                col = self.table[col_name]
                # is_singleton = (count over partition == 1) and not null
                win = ibis.window(group_by=col)
                mutates[f"{col_name}__is_singleton"] = (
                    (col.count().over(win) == 1) & col.notnull()
                ).cast("int")

            m = self.table.mutate(**mutates)
            aggs = [
                m[f"{col_name}__is_singleton"].sum().name(f"{col_name}__n_unique")
                for col_name in batch_cols
            ]
            batches.append(m.aggregate(aggs))

        return batches

    def build_complex_metrics(
        self,
        override_types: dict[str, str] | None = None,
        variables_metadata: dict[str, dict] | None = None,
    ) -> list[tuple[str, str, ir.Expr, str]]:
        """
        Returns a list of (column_name, metric_name, expression, execution_hint)
        where execution_hint is 'Value' (scalar) or 'Table' (result set).
        """
        schema = self.table.schema()
        plans = []
        overrides = override_types or {}
        metadata = variables_metadata or {}

        for col_name, dtype in schema.items():
            col = self.table[col_name]
            mapped_type = overrides.get(col_name)
            col_meta = metadata.get(col_name, {})

            # 1. n_unique (singletons) - Scalar Value
            # DEPRECATED in complex pass: now batched in run() or global pass
            # We omit it here to avoid individual database round-trips.

            # 2. Histograms / Distribution (top values) - Table
            is_discrete = mapped_type == "Categorical" or not isinstance(
                dtype, (dt.Integer, dt.Floating, dt.Decimal)
            )
            is_hashable = not isinstance(dtype, (dt.Array, dt.Map, dt.Struct))

            if is_discrete and is_hashable:
                vc = col.value_counts()
                count_col = vc.columns[1]
                hist_expr = vc.order_by(ibis.desc(count_col)).rename({"count": count_col}).limit(20)
                plans.append((col_name, "top_values", hist_expr, "Table"))

            # 3. Extreme Values (Smallest/Largest) - Table
            if not isinstance(dtype, (dt.Array, dt.Map, dt.Struct)):
                # Heuristic: If cardinality is low, use distinct() to speed up sort
                n_distinct = col_meta.get("n_distinct")
                n_total = col_meta.get("n", 0)
                use_distinct = False
                if (
                    isinstance(n_distinct, (int, float))
                    and n_total > 0
                    and (n_distinct / n_total) <= 0.5
                ):
                    use_distinct = True

                base_table = self.table.select(col_name)
                if use_distinct:
                    base_table = base_table.distinct()

                # Smallest
                small_expr = (
                    base_table.filter(base_table[col_name].notnull())
                    .order_by(base_table[col_name])
                    .limit(5)
                )
                plans.append((col_name, "extreme_values_smallest", small_expr, "Table"))

                # Largest
                large_expr = (
                    base_table.filter(base_table[col_name].notnull())
                    .order_by(ibis.desc(base_table[col_name]))
                    .limit(5)
                )
                plans.append((col_name, "extreme_values_largest", large_expr, "Table"))

            # 4. String Length Histogram - Table
            if isinstance(dtype, dt.String):
                len_hist = col.length().value_counts().limit(10)
                plans.append((col_name, "length_histogram", len_hist, "Table"))

        return plans
