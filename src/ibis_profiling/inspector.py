import ibis
import ibis.expr.datatypes as dt


class DatasetInspector:
    def __init__(self, table: ibis.Table):
        self.table = table
        self.schema = table.schema()

    def get_column_types(self) -> dict[str, dt.DataType]:
        return {name: dtype for name, dtype in self.schema.items()}

    def estimate_memory_size(self, row_count: int) -> int:
        """
        Estimates the memory footprint of the dataset based on schema and row count.
        """
        total_bytes_per_row = 0
        for dtype in self.schema.values():
            if isinstance(dtype, (dt.Int64, dt.Float64, dt.Timestamp)):
                total_bytes_per_row += 8
            elif isinstance(dtype, (dt.Int32, dt.Float32, dt.Date)):
                total_bytes_per_row += 4
            elif isinstance(dtype, (dt.Int16, dt.UInt16)):
                total_bytes_per_row += 2
            elif isinstance(dtype, (dt.Int8, dt.UInt8, dt.Boolean)):
                total_bytes_per_row += 1
            elif isinstance(dtype, dt.String):
                # We use a 20-byte heuristic for strings
                total_bytes_per_row += 20
            else:
                # Fallback for complex types
                total_bytes_per_row += 16

        return total_bytes_per_row * row_count

    def is_hashable(self, col_name: str) -> bool:
        """Determines if a column type is hashable (stable)."""
        dtype = self.schema[col_name]
        return not isinstance(dtype, (dt.Array, dt.Map, dt.Struct))
