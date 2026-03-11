import ibis
from ibis_profiling.inspector import DatasetInspector


def test_memory_estimation():
    schema = ibis.schema({"a": "int64", "b": "float64", "c": "string", "d": "boolean"})
    table = ibis.memtable([{"a": 1, "b": 1.0, "c": "hello", "d": True}], schema=schema)

    inspector = DatasetInspector(table)

    # Estimate for 1000 rows
    size = inspector.estimate_memory_size(1000)

    # int64 (8) + float64 (8) + string (avg 20) + boolean (1) = 37 bytes per row
    # 37 * 1000 = 37000
    assert size == 37000


def test_hashable_detection():
    schema = ibis.schema({"a": "int64", "b": "array<int64>"})
    table = ibis.table(schema, name="t")
    inspector = DatasetInspector(table)

    assert inspector.is_hashable("a") is True
    assert inspector.is_hashable("b") is False
