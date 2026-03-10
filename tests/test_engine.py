import ibis
import pandas as pd
from ibis_profiling.engine import ExecutionEngine


def test_engine_execution():
    engine = ExecutionEngine()
    con = ibis.duckdb.connect()
    # con.sql("SELECT 1 AS a").execute() # This is already pandas-like or arrow

    plan = con.sql("SELECT 1 AS a")
    result = engine.execute(plan)

    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]["a"] == 1
