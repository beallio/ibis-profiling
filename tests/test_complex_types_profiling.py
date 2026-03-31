import ibis
import ibis.expr.datatypes as dt
import pytest
from ibis_profiling import ProfileReport


def test_profiling_complex_types_no_crash():
    con = ibis.duckdb.connect()

    # Create a table with complex types
    # Array and JSON are known to cause issues with nunique in some backends
    schema = ibis.schema(
        {
            "id": dt.int64,
            "arr_col": dt.Array(dt.int64),
            "json_col": dt.json,
            "map_col": dt.Map(dt.string, dt.int64),
        }
    )

    import pandas as pd

    df = pd.DataFrame(
        [
            {"id": 1, "arr_col": [1, 2], "json_col": '{"a": 1}', "map_col": {"x": 1}},
            {"id": 2, "arr_col": [3, 4], "json_col": '{"b": 2}', "map_col": {"y": 2}},
        ]
    )

    # We must cast the columns explicitly in ibis because pandas might object
    # or use memtable
    table = ibis.memtable(df, schema=schema)

    try:
        # This should not crash
        report = ProfileReport(table)
        data = report.to_dict()

        # Verify columns exist in report
        assert "arr_col" in data["variables"]
        assert "json_col" in data["variables"]

        arr_stats = data["variables"]["arr_col"]
        json_stats = data["variables"]["json_col"]
        map_stats = data["variables"]["map_col"]

        # In current implementation, if not in aggregation, it won't be in variables
        # or will be None/0 depending on how finalize() handles it.
        # Given it's skipped in global aggregation, it should NOT have a value here.
        # Actually, finalize() might compute p_distinct if n_distinct exists.
        assert arr_stats.get("n_distinct") is None or arr_stats.get("n_distinct") == 0
        assert json_stats.get("n_distinct") is None or json_stats.get("n_distinct") == 0
        assert map_stats.get("n_distinct") is None or map_stats.get("n_distinct") == 0

    except Exception as e:
        pytest.fail(f"Profiling complex types crashed: {e}")
    finally:
        con.disconnect()


if __name__ == "__main__":
    test_profiling_complex_types_no_crash()
