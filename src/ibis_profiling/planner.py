import ibis
import ibis.expr.types as ir
import ibis.expr.datatypes as dt
from .metrics import MetricRegistry, MetricCategory


class QueryPlanner:
    def __init__(
        self,
        table: ibis.Table,
        registry: MetricRegistry,
        use_sketches: bool = False,
        n_unique_threshold: int = 50_000_000,
    ):
        self.table = table
        self.registry = registry
        self.use_sketches = use_sketches
        self.n_unique_threshold = n_unique_threshold

    def build_global_aggregation(self) -> ir.Table:
        """Batches all applicable simple COLUMN metrics into a single aggregation query."""
        schema = self.table.schema()
        aggs = []

        # Check for sketch support (currently DuckDB)
        is_duckdb = False
        try:
            is_duckdb = self.table.get_backend().name == "duckdb"
        except Exception:
            pass

        for col_name, dtype in schema.items():
            col = self.table[col_name]

            # Always include total count for thresholding
            aggs.append(col.count().name(f"{col_name}__n"))

            for metric in self.registry.metrics.values():
                # We skip n_unique (singletons) for now as it's complex (requires value_counts)
                if metric.name == "n_unique":
                    continue

                if metric.category == MetricCategory.COLUMN and metric.supports(dtype):
                    # Special case: n_distinct can be sketched
                    if metric.name == "n_distinct" and self.use_sketches and is_duckdb:
                        expr = col.approx_nunique()
                    else:
                        expr = metric.build_expr(col)

                    # We namespace the alias to reconstruct the report later
                    expr_alias = f"{col_name}__{metric.name}"
                    aggs.append(expr.name(expr_alias))

        # Include dataset-wide metrics
        aggs.append(self.table.count().name("_dataset__row_count"))

        # We'll omit distinct count from this global batch to avoid IntegrityErrors
        # and handle it in __init__.py as a separate pass.

        return self.table.aggregate(aggs)

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

            # 1. n_unique (singletons) - Scalar Value (but uses subquery, so hint Table)
            metric = self.registry.metrics.get("n_unique")
            if metric and metric.supports(dtype):
                n_total = col_meta.get("n") or 0
                n_distinct = col_meta.get("n_distinct")
                n_missing = col_meta.get("n_missing") or 0
                n_rows = n_total - n_missing

                # Skip if above threshold (prohibitively expensive value_counts)
                # Treat unknown n_distinct (None or 0 with large n) as needing skip
                skip = False
                if self.n_unique_threshold > 0 and n_total > self.n_unique_threshold:
                    if (
                        n_distinct is None
                        or not isinstance(n_distinct, (int, float))
                        or n_distinct > self.n_unique_threshold
                    ):
                        skip = True

                if skip:
                    # We return None for the expression to indicate it was skipped
                    plans.append((col_name, metric.name, None, "Table"))
                # Optimization: if all values are distinct, n_unique is exactly n_distinct
                elif n_rows > 0 and n_distinct == n_rows:
                    # We return a literal scalar expression
                    plans.append((col_name, metric.name, ibis.literal(n_distinct), "Value"))
                else:
                    plans.append((col_name, metric.name, metric.build_expr(col), "Table"))

            # 2. Histograms / Distribution (top values) - Table
            is_discrete = mapped_type == "Categorical" or not isinstance(
                dtype, (dt.Integer, dt.Floating, dt.Decimal)
            )
            is_hashable = not isinstance(dtype, (dt.Array, dt.Map, dt.Struct, dt.JSON))

            if is_discrete and is_hashable:
                n_total = col_meta.get("n") or 0
                n_distinct = col_meta.get("n_distinct")

                # Guard top_values with threshold as well
                skip = False
                if self.n_unique_threshold > 0 and n_total > self.n_unique_threshold:
                    if (
                        n_distinct is None
                        or not isinstance(n_distinct, (int, float))
                        or n_distinct > self.n_unique_threshold
                    ):
                        skip = True

                if skip:
                    plans.append((col_name, "top_values", None, "Table"))
                else:
                    vc = col.value_counts()
                    count_col = vc.columns[1]
                    hist_expr = vc.order_by(ibis.desc(count_col)).limit(20)
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
