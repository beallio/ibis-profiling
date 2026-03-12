import ibis
from datetime import datetime
from .inspector import DatasetInspector
from .metrics import registry
from .planner import QueryPlanner
from .engine import ExecutionEngine
from .report import ProfileReport as InternalProfileReport


def profile(
    table: ibis.Table, minimal: bool = False, title: str = "Ibis Profiling Report"
) -> InternalProfileReport:
    """
    Main entrypoint for profiling an Ibis table.

    This function:
    1. Inspects the table schema.
    2. Plans a minimal set of batched aggregation queries.
    3. Executes the queries in the backend.
    4. Formats the results into a structured report.
    """
    start_time = datetime.now()
    inspector = DatasetInspector(table)
    planner = QueryPlanner(table, registry)
    engine = ExecutionEngine()

    # 1. Generate and execute simple aggregates (1 pass)
    global_plan = planner.build_global_aggregation()
    raw_results = engine.execute(global_plan)

    # 2. Collect Table Metadata (Memory, etc.)
    row_count = raw_results["_dataset__row_count"][0] if not raw_results.is_empty() else 0
    mem_size = engine.get_storage_size(table)
    if mem_size is None:
        mem_size = inspector.estimate_memory_size(row_count)

    col_types = inspector.get_column_types()
    # Inject dataset metadata into schema for the Report model to pick up
    col_types["_dataset"] = {
        "memory_size": mem_size,
        "record_size": mem_size / row_count if row_count > 0 else 0,
    }

    # 3. Build base report
    report = InternalProfileReport(raw_results, col_types, title=title)
    report.analysis["date_start"] = start_time.isoformat()

    # 4. Inject column-level static metadata (hashable)
    for col_name in report.variables:
        if col_name != "_dataset":
            report.variables[col_name]["hashable"] = inspector.is_hashable(col_name)

    # 5. Handle dataset-wide distinct count (Duplicates)
    # We do this separately to avoid IntegrityErrors in the global batch
    if not minimal:
        n_distinct_rows = table.distinct().count().execute()
        report.table["n_distinct_rows"] = n_distinct_rows
        n_total = report.table.get("n", 0)
        report.table["n_duplicates"] = n_total - n_distinct_rows
        report.table["p_duplicates"] = (n_total - n_distinct_rows) / n_total if n_total > 0 else 0

    # 4. Handle advanced moments (Skewness, MAD) in a second pass if possible
    # We use mean/std from pass 1 to avoid nesting issues
    if not minimal:
        second_pass_aggs = []
        numeric_cols = [c for c, s in report.variables.items() if s.get("type") == "Numeric"]
        for col_name in numeric_cols:
            stats = report.variables[col_name]
            mean = stats.get("mean")
            std = stats.get("std")
            col = table[col_name]

            # Skewness
            if mean is not None and std is not None and std > 0:
                skew_expr = ((col - mean) / std).pow(3).mean().name(f"{col_name}__skewness")
                second_pass_aggs.append(skew_expr)

            # MAD
            if mean is not None:
                mad_expr = (col - mean).abs().mean().name(f"{col_name}__mad")
                second_pass_aggs.append(mad_expr)

        if second_pass_aggs:
            results = table.aggregate(second_pass_aggs).to_pyarrow().to_pydict()
            for k, v in results.items():
                parts = k.split("__")
                c_name, m_name = parts[0], parts[1]
                report.add_metric(c_name, m_name, v[0])

    # 4. Handle complex metrics (e.g. n_unique, top_values)
    complex_plans = planner.build_complex_metrics()
    for col_name, metric_name, expr in complex_plans:
        if isinstance(expr, ibis.expr.types.Table):
            # For table-valued metrics like top_values
            val = expr.to_pyarrow().to_pydict()
        else:
            # For scalar-valued metrics like n_unique
            val = expr.to_pyarrow().as_py()
        report.add_metric(col_name, metric_name, val)

    # 4. Handle Correlations
    if not minimal:
        from .report.model.correlations import CorrelationEngine

        numeric_cols = [c for c, s in report.variables.items() if s.get("type") == "Numeric"]
        if len(numeric_cols) >= 2:
            # 4a. Pearson (Simple Aggregates)
            corr_results = CorrelationEngine._compute_pearson(table, numeric_cols)
            flat_exprs = []
            for i, row in enumerate(corr_results["matrix"]):
                for j, item in enumerate(row):
                    if isinstance(item, ibis.expr.types.Scalar):
                        flat_exprs.append(item.name(f"corr_pearson_{i}_{j}"))

            if flat_exprs:
                executed_vals = table.aggregate(flat_exprs).to_pyarrow().to_pydict()
                final_matrix = []
                val_idx = 0
                for i, row in enumerate(corr_results["matrix"]):
                    new_row = []
                    for j, item in enumerate(row):
                        if i == j:
                            new_row.append(1.0)
                        else:
                            key = list(executed_vals.keys())[val_idx]
                            new_row.append(executed_vals[key][0])
                            val_idx += 1
                    final_matrix.append(new_row)
                report.correlations["pearson"] = {"columns": numeric_cols, "matrix": final_matrix}

            # 4b. Spearman (Rank Pass)
            spearman_meta = CorrelationEngine._compute_spearman(table, numeric_cols)
            rank_exprs = [spearman_meta["rank_exprs"][c].name(f"rank_{c}") for c in numeric_cols]
            # Create a CTE-like table with ranks
            rank_table = table.mutate(rank_exprs)

            flat_spearman = []
            for i, c1 in enumerate(numeric_cols):
                for j, c2 in enumerate(numeric_cols):
                    if i < j:
                        r1 = rank_table[f"rank_{c1}"]
                        r2 = rank_table[f"rank_{c2}"]
                        # Pearson on Ranks
                        expr = r1.cov(r2, how="pop") / (r1.std(how="pop") * r2.std(how="pop"))
                        flat_spearman.append(expr.name(f"corr_spearman_{i}_{j}"))

            if flat_spearman:
                executed_vals = rank_table.aggregate(flat_spearman).to_pyarrow().to_pydict()
                final_matrix = [[1.0 for _ in numeric_cols] for _ in numeric_cols]
                val_idx = 0
                for i in range(len(numeric_cols)):
                    for j in range(len(numeric_cols)):
                        if i < j:
                            key = list(executed_vals.keys())[val_idx]
                            val = executed_vals[key][0]
                            final_matrix[i][j] = val
                            final_matrix[j][i] = val
                            val_idx += 1
                report.correlations["spearman"] = {"columns": numeric_cols, "matrix": final_matrix}

    # 5. Handle Monotonicity and other column-wise complex checks
    if not minimal:
        numeric_cols = [c for c, s in report.variables.items() if s.get("type") == "Numeric"]
        # Monotonicity check requires a window pass
        # We must perform the comparison IN the window pass (mutate) then aggregate
        mono_checks = []
        for col_name in numeric_cols:
            col = table[col_name]
            prev = col.lag().over(ibis.window())
            mono_checks.append(((col >= prev) | prev.isnull()).name(f"inc_{col_name}"))
            mono_checks.append(((col <= prev) | prev.isnull()).name(f"dec_{col_name}"))

        if mono_checks:
            check_table = table.mutate(mono_checks)
            final_aggs = []
            for col_name in numeric_cols:
                final_aggs.append(
                    check_table[f"inc_{col_name}"].all().name(f"{col_name}__monotonic_increasing")
                )
                final_aggs.append(
                    check_table[f"dec_{col_name}"].all().name(f"{col_name}__monotonic_decreasing")
                )

            results = check_table.aggregate(final_aggs).to_pyarrow().to_pydict()
            for k, v in results.items():
                parts = k.split("__")
                c_name, m_name = parts[0], parts[1]
                report.add_metric(c_name, m_name, v[0])

    # 6. Capture Samples (Head)
    # Note: Ibis doesn't have a reliable cross-backend 'tail' without an order key.
    # We'll just capture the head for now.
    head_sample = table.head(10).to_pyarrow().to_pydict()
    report.add_metric("_dataset", "head", head_sample)

    # 6. Missing Values (Matrix/Heatmap)
    if not minimal:
        from .report.model.missing import MissingEngine

        report.missing = MissingEngine.compute(table, report.variables)

    end_time = datetime.now()
    report.analysis["date_end"] = end_time.isoformat()
    report.analysis["duration"] = (end_time - start_time).total_seconds() * 1000

    return report


class ProfileReport:
    """
    Compatibility wrapper to mimic ydata-profiling API.
    """

    def __init__(self, table: ibis.Table, minimal: bool = False, **kwargs):
        title = kwargs.get("title", "Ibis Profiling Report")
        self._report = profile(table, minimal=minimal, title=title)

    def to_file(self, output_file: str):
        return self._report.to_file(output_file)

    def to_json(self) -> str:
        return self._report.to_json()

    def to_dict(self) -> dict:
        return self._report.to_dict()

    def get_description(self) -> dict:
        return self._report.get_description()

    def to_html(self, template: str = "ydata") -> str:
        return self._report.to_html(template=template)


__all__ = ["profile", "registry", "ProfileReport"]
