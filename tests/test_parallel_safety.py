import ibis
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from ibis_profiling import Profiler


def test_parallel_fallback_warning():
    # DuckDB is NOT in the allowlist
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


def test_check_parallel_safety_logic():
    # All backends should currently trigger a fallback for safety

    data = {"col_1": [1]}
    table = ibis.memtable(pd.DataFrame(data))
    profiler = Profiler(table, parallel=True)

    # 1. Test Pandas (used to be allowed, now should be unsafe)
    with patch("ibis.expr.types.relations.Table.get_backend") as mock_get_backend:
        mock_con = MagicMock()
        mock_con.name = "pandas"
        mock_get_backend.return_value = mock_con
        assert profiler._check_parallel_safety() == "pandas"

    # 2. Test Postgres (not allowlisted)
    with patch("ibis.expr.types.relations.Table.get_backend") as mock_get_backend:
        mock_con = MagicMock()
        mock_con.name = "postgres"
        mock_get_backend.return_value = mock_con
        assert profiler._check_parallel_safety() == "postgres"

    # 3. Test Unknown
    with patch("ibis.expr.types.relations.Table.get_backend") as mock_get_backend:
        mock_get_backend.side_effect = Exception("Unknown")
        assert profiler._check_parallel_safety() == "unknown"


def test_run_sequential_fallback_mock():
    # Test that run() respects the safety check
    data = {"col_1": [1]}
    table = ibis.memtable(pd.DataFrame(data))
    profiler = Profiler(table, parallel=True)

    with patch.object(profiler, "_check_parallel_safety", return_value="some_unsafe_db"):
        report = profiler.run()
        assert profiler.parallel is False
        assert profiler.executor is None
        assert any(
            "Parallel mode disabled for some_unsafe_db" in w
            for w in report.analysis.get("warnings", [])
        )
