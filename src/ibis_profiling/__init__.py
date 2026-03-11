import ibis
from .inspector import DatasetInspector
from .metrics import registry
from .planner import QueryPlanner
from .engine import ExecutionEngine
from .report import ProfileReport as InternalProfileReport


def profile(table: ibis.Table) -> InternalProfileReport:
    """
    Main entrypoint for profiling an Ibis table.

    This function:
    1. Inspects the table schema.
    2. Plans a minimal set of batched aggregation queries.
    3. Executes the queries in the backend.
    4. Formats the results into a structured report.
    """
    inspector = DatasetInspector(table)
    planner = QueryPlanner(table, registry)
    engine = ExecutionEngine()

    # 1. Generate and execute simple aggregates (1 pass)
    global_plan = planner.build_global_aggregation()
    raw_results = engine.execute(global_plan)

    # 2. Build base report
    report = InternalProfileReport(raw_results, inspector.get_column_types())

    # 3. Handle dataset-wide distinct count (Duplicates)
    # We do this separately to avoid IntegrityErrors in the global batch
    n_distinct_rows = table.distinct().count().execute()
    report.table["n_distinct_rows"] = n_distinct_rows
    n_total = report.table.get("n", 0)
    report.table["n_duplicates"] = n_total - n_distinct_rows
    report.table["p_duplicates"] = (n_total - n_distinct_rows) / n_total if n_total > 0 else 0

    # 4. Handle advanced moments (Skewness, MAD) in a second pass if possible
    # We use mean/std from pass 1 to avoid nesting issues
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
    from .report.model.correlations import CorrelationEngine

    numeric_cols = [c for c, s in report.variables.items() if s.get("type") == "Numeric"]
    if len(numeric_cols) >= 2:
        # Build correlation expressions
        corr_results = CorrelationEngine._compute_pearson(table, numeric_cols)
        # Execute matrix (this could be optimized into a single batch)
        # For now, we execute row by row or flat
        flat_exprs = []
        for row in corr_results["matrix"]:
            for item in row:
                if isinstance(item, ibis.expr.types.Scalar):
                    flat_exprs.append(item)

        if flat_exprs:
            # Aggregate all correlations in one go
            executed_vals = table.aggregate(flat_exprs).to_pyarrow().to_pydict()

            # Map results back to matrix
            final_matrix = []
            val_idx = 0
            for i, row in enumerate(corr_results["matrix"]):
                new_row = []
                for j, item in enumerate(row):
                    if i == j:
                        new_row.append(1.0)
                    else:
                        # Use the key from the executed aggregate (usually the col name if alias exists, but here we didn't alias)
                        # Ibis aggregate usually returns keys like 'corr(col1, col2)'
                        # Better to use a controlled indexing
                        key = list(executed_vals.keys())[val_idx]
                        new_row.append(executed_vals[key][0])
                        val_idx += 1
                final_matrix.append(new_row)

            report.correlations["pearson"] = {"columns": numeric_cols, "matrix": final_matrix}

    # 5. Capture Samples (Head)
    # Note: Ibis doesn't have a reliable cross-backend 'tail' without an order key.
    # We'll just capture the head for now.
    head_sample = table.head(10).to_pyarrow().to_pydict()
    report.add_metric("_dataset", "head", head_sample)

    # 6. Missing Values (Matrix/Heatmap)
    from .report.model.missing import MissingEngine

    report.missing = MissingEngine.compute(table, report.variables)

    return report


class ProfileReport:
    """
    Compatibility wrapper to mimic ydata-profiling API.
    """

    def __init__(self, table: ibis.Table, **kwargs):
        # kwargs ignored for now, just for signature compatibility
        self._report = profile(table)

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
