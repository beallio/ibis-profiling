import ibis
import ibis.expr.datatypes as dt
from ibis_profiling.inspector import DatasetInspector


def test_dataset_inspector():
    schema = ibis.schema({"a": dt.Int64(), "b": dt.String()})
    table = ibis.table(schema, name="test")

    inspector = DatasetInspector(table)
    types = inspector.get_column_types()

    assert types["a"] == dt.Int64()
    assert types["b"] == dt.String()
    assert len(types) == 2
