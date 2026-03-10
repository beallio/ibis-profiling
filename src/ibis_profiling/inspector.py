import ibis


class DatasetInspector:
    def __init__(self, table: ibis.Table):
        self.table = table
        self.schema = table.schema()

    def get_column_types(self) -> dict[str, ibis.expr.datatypes.DataType]:
        return {name: dtype for name, dtype in self.schema.items()}
