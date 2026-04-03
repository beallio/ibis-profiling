import ibis
from ibis_profiling.memory import MemoryManager


def test_calculate_batch_size():
    # Small dataset: should be 500
    assert MemoryManager.calculate_batch_size(1000, 10) == 500

    # 50M cells: should be 100
    assert MemoryManager.calculate_batch_size(5_000_000, 10) == 100

    # 200M cells: should be 50
    assert MemoryManager.calculate_batch_size(10_000_000, 20) == 50

    # Massive dataset (>500M cells): should be 20
    assert MemoryManager.calculate_batch_size(20_000_000, 50) == 20


def test_to_int():
    assert MemoryManager.to_int(10) == 10
    assert MemoryManager.to_int("10") == 10
    assert MemoryManager.to_int(None) == 0

    # Mock an object with .item() (like numpy scalar)
    class MockItem:
        def item(self):
            return 42

    assert MemoryManager.to_int(MockItem()) == 42

    # Mock a list-like object
    assert MemoryManager.to_int([5]) == 5


def test_apply_duckdb_limits():
    con = ibis.duckdb.connect()
    # Should not raise
    MemoryManager.apply_duckdb_limits(con, available_mb=1024)

    # Check if we can verify the limit (DuckDB specific SQL)
    res = (
        con.sql("SELECT VALUE FROM duckdb_settings() WHERE name = 'memory_limit'")
        .to_pyarrow()
        .to_pydict()
    )
    # The heuristic uses 70% of available RAM. 70% of 1024MB is ~716MB.
    # DuckDB reports this in MiB (682.8 MiB).
    limit_val = str(res["value"][0])
    assert "MiB" in limit_val or "MB" in limit_val
    # Check that it's in the right ballpark (approx 70% of 1024MB)
    numeric_part = float(limit_val.split()[0])
    assert 650 <= numeric_part <= 750 or 700 <= numeric_part <= 730
