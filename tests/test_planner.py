import ibis
import ibis.expr.datatypes as dt
from ibis_profiling.planner import QueryPlanner
from ibis_profiling.metrics import registry


def test_planner_aggregation_building():
    schema = ibis.schema({"a": dt.Int64()})
    table = ibis.table(schema, name="test")

    planner = QueryPlanner(table, registry)
    plan = planner.build_global_aggregation()

    # Check the aggregated columns
    # We expect columns like "a__mean", "a__min", etc. and "_dataset__row_count"
    plan_schema = plan.schema()

    assert "a__mean" in plan_schema
    assert "a__min" in plan_schema
    assert "_dataset__row_count" in plan_schema
