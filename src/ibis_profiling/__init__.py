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

    # 3. Handle complex metrics (e.g. n_unique)
    # Note: For performance, we could batch these in QueryPlanner if possible,
    # but currently they are separate expressions.
    complex_plans = planner.build_complex_metrics()
    for col_name, metric_name, expr in complex_plans:
        val = expr.to_pyarrow().as_py()
        report.add_metric(col_name, metric_name, val)

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

    def to_html(self) -> str:
        return self._report.to_html()


__all__ = ["profile", "registry", "ProfileReport"]
