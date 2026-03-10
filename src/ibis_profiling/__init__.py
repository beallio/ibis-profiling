import ibis
from .inspector import DatasetInspector
from .metrics import registry
from .planner import QueryPlanner
from .engine import ExecutionEngine
from .report import ProfileReport


def profile(table: ibis.Table) -> ProfileReport:
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
    report = ProfileReport(raw_results, inspector.get_column_types())

    # 3. Handle complex metrics (e.g. n_unique)
    # Note: For performance, we could batch these in QueryPlanner if possible,
    # but currently they are separate expressions.
    complex_plans = planner.build_complex_metrics()
    for col_name, metric_name, expr in complex_plans:
        val = expr.to_pyarrow().as_py()
        report.add_metric(col_name, metric_name, val)

    return report


__all__ = ["profile", "registry"]
