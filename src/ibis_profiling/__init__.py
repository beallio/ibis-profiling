import ibis
from .inspector import DatasetInspector
from .metrics import registry
from .planner import QueryPlanner
from .engine import ExecutionEngine
from .report import ProfileReport


def profile(table: ibis.Table) -> dict:
    """
    Main entry point for profiling an Ibis table.

    This function:
    1. Inspects the table schema.
    2. Plans a minimal set of batched aggregation queries.
    3. Executes the queries in the backend.
    4. Formats the results into a structured report.
    """
    inspector = DatasetInspector(table)
    planner = QueryPlanner(table, registry)
    engine = ExecutionEngine()

    # Generate the query plan (0 execution time)
    global_plan = planner.build_global_aggregation()

    # Push computation to the backend (1 massive batched query)
    raw_results = engine.execute(global_plan)

    # Interpret the results
    report = ProfileReport(raw_results, inspector.get_column_types())

    return report.to_dict()


__all__ = ["profile", "registry"]
