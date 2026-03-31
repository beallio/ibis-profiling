import ibis
import ibis.expr.datatypes as dt
from ibis_profiling.planner import QueryPlanner
from ibis_profiling.metrics import registry


def test_harden_planner_skip_unknown_distinct():
    con = ibis.duckdb.connect()
    schema = ibis.schema({"huge_col": dt.string, "json_col": dt.json})
    table = con.create_table("test_harden", schema=schema, temp=True)

    planner = QueryPlanner(table, registry, n_unique_threshold=1000)

    # 1. Test skip when n_distinct is missing (unknown) but n_total > threshold
    metadata = {
        "huge_col": {"n": 2000}  # n_distinct is missing
    }

    plans = planner.build_complex_metrics(variables_metadata=metadata)

    # Extract plan for huge_col n_unique and top_values
    huge_n_unique = next((p for p in plans if p[0] == "huge_col" and p[1] == "n_unique"), None)
    huge_top_values = next((p for p in plans if p[0] == "huge_col" and p[1] == "top_values"), None)

    assert huge_n_unique is not None
    # Current behavior: if n_distinct is missing, it defaults to 0, and 0 is NOT > 1000, so it DOES NOT skip.
    # We WANT it to skip if n_distinct is unknown and n > threshold.
    assert huge_n_unique[2] is None, (
        "Should skip n_unique when n_distinct is unknown and n > threshold"
    )
    assert huge_top_values[2] is None, (
        "Should skip top_values when n_distinct is unknown and n > threshold"
    )


def test_harden_planner_json_non_hashable():
    con = ibis.duckdb.connect()
    schema = ibis.schema({"json_col": dt.json})
    table = con.create_table("test_json", schema=schema, temp=True)

    planner = QueryPlanner(table, registry)

    plans = planner.build_complex_metrics()

    # top_values should only be planned for hashable types
    json_top_values = next((p for p in plans if p[0] == "json_col" and p[1] == "top_values"), None)

    # Current behavior might include JSON if it's not explicitly in the exclusion list
    assert json_top_values is None, "JSON should be treated as non-hashable"


if __name__ == "__main__":
    test_harden_planner_skip_unknown_distinct()
    test_harden_planner_json_non_hashable()
