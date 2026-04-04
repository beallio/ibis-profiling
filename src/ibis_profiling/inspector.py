import ibis
import ibis.expr.datatypes as dt
from .logical_types import IbisLogicalTypeSystem


class DatasetInspector:
    """Handles dataset-wide heuristics and metadata analysis."""

    def __init__(
        self,
        table: ibis.Table,
        minimal: bool = False,
        n_unique_threshold: int = 100_000,
        inference_sample_size: int | None = 10_000,
        row_count: int | None = None,
    ):
        self.table = table
        self.minimal = minimal
        self.n_unique_threshold = n_unique_threshold
        self.row_count = row_count
        self.type_system = IbisLogicalTypeSystem(
            minimal=minimal,
            n_unique_threshold=n_unique_threshold,
            inference_sample_size=inference_sample_size,
            row_count=row_count,
        )

    def get_logical_types(self):
        return self.type_system.infer_all_types(self.table)

    def is_hashable(self, column_name: str) -> bool:
        """Determines if a column can be used in group-by/distinct operations."""
        dtype = self.table[column_name].type()
        return not isinstance(dtype, (dt.Array, dt.Map, dt.Struct, dt.JSON))

    def get_column_types(self) -> dict:
        return {name: self.table[name].type() for name in self.table.columns}

    def estimate_memory_size(self, row_count: int) -> int:
        """
        Rough heuristic for memory size based on schema and row count.
        Used as fallback if backend doesn't provide physical size.
        """
        schema = self.table.schema()
        total_bytes_per_row = 0

        for dtype in schema.values():
            if isinstance(dtype, dt.Integer):
                total_bytes_per_row += 8
            elif isinstance(dtype, dt.Floating):
                total_bytes_per_row += 8
            elif isinstance(dtype, dt.Boolean):
                total_bytes_per_row += 1
            elif isinstance(dtype, dt.String):
                # We use a 20-byte heuristic for strings
                total_bytes_per_row += 20
            else:
                # Fallback for complex types
                total_bytes_per_row += 16

        return total_bytes_per_row * row_count
