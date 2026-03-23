import ibis
import duckdb
from ibis_profiling.engine import ExecutionEngine


def test_duckdb_storage_size_integration():
    """Verify get_storage_size with a real DuckDB connection."""
    con = ibis.duckdb.connect()
    df = ibis.memtable({"i": list(range(1000))})
    con.create_table("test_table_real", df.execute())

    engine = ExecutionEngine()
    t = con.table("test_table_real")

    size = engine.get_storage_size(t)
    # DuckDB currently returns None by design due to column mismatch in pragma_storage_info
    assert size is None

    # Verify that it doesn't crash with malicious input
    class MockOp:
        def __init__(self, name):
            self.name = name

    class MockTable:
        def op(self):
            return MockOp("'); DROP TABLE students; --")

        def _find_backend(self):
            return con

    # This should return None without error
    assert engine.get_storage_size(MockTable()) is None


def test_duckdb_parameterized_call():
    """Verify that DuckDB handles parameterized calls safely."""
    con = duckdb.connect()
    con.execute("CREATE TABLE test_param (i INT)")

    # Injection attempt should fail (because literal name not found)
    # or return empty result, but NOT execute the injection.
    try:
        # If it were vulnerable, this would DROP the table
        con.execute("CALL pragma_storage_info(?)", ["'); DROP TABLE test_param; --"])
    except Exception as e:
        assert "does not exist" in str(e)

    # Table should still exist
    res = con.execute("SELECT * FROM test_param").fetchall()
    assert len(res) == 0
