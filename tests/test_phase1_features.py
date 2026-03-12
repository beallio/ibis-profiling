import ibis
from ibis_profiling import ProfileReport


def test_phase1_table_meta():
    schema = ibis.schema({"a": "int64", "b": "string"})
    # Create a table with 10 rows
    data = [{"a": i, "b": f"val_{i}"} for i in range(10)]
    table = ibis.memtable(data, schema=schema)

    report = ProfileReport(table, minimal=True)
    description = report.get_description()

    # Table level
    assert "memory_size" in description["table"]
    assert "record_size" in description["table"]
    # int64(8) + string(20) = 28 * 10 = 280
    assert description["table"]["memory_size"] == 280
    assert description["table"]["record_size"] == 28.0

    # Variable level
    assert description["variables"]["a"]["hashable"] is True
    assert description["variables"]["b"]["hashable"] is True

    # Verify no _dataset in variables
    assert "_dataset" not in description["variables"]
