import ibis
import pandas as pd
import numpy as np
from ibis_profiling import Profiler


def test_parallel_fallback_warning():
    # DuckDB is flagged as UNSAFE_BACKENDS in our implementation
    num_cols = 5
    num_rows = 100
    data = {f"col_{i}": np.random.randn(num_rows) for i in range(num_cols)}
    df = pd.DataFrame(data)

    con = ibis.duckdb.connect()
    t = con.create_table("test_table_parallel", df)

    # Request parallel mode
    profiler = Profiler(t, parallel=True, pool_size=4)

    # Run profiling
    report = profiler.run()

    # Verify fallback occurred
    assert profiler.parallel is False
    assert profiler.executor is None

    # Verify warning is in report
    warnings = report.analysis.get("warnings", [])
    assert any("Parallel mode disabled for duckdb backend" in w for w in warnings)
