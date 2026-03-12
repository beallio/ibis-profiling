import ibis
import polars as pl
from ibis_profiling.engine import ExecutionEngine


def test_engine_execution():
    engine = ExecutionEngine()
    con = ibis.duckdb.connect()

    plan = con.sql("SELECT 1 AS a")
    result = engine.execute(plan)

    assert isinstance(result, pl.DataFrame)
    assert result.row(0, named=True)["a"] == 1
