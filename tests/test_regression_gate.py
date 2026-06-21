import pytest

from tools.regression import gate


@pytest.mark.slow
def test_profiler_regression_gate(tmp_path):
    try:
        import ibis
        import polars as pl

        probe_path = tmp_path / "regression-gate-probe.parquet"
        pl.DataFrame({"value": [1]}).write_parquet(probe_path)
        probe = ibis.duckdb.connect().read_parquet(probe_path)
        probe.count().execute()
    except Exception as exc:
        pytest.skip(f"DuckDB/parquet path is unavailable: {exc}")

    assert gate.run_check() == [], (
        "Profiler JSON differs from tools/regression/baseline_2M_20col.json. "
        "Inspect tools/regression/gate.py for the deterministic comparison surface."
    )
