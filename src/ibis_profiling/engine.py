import ibis
import ibis.expr.types as ir
import polars as pl
from typing import cast


class ExecutionEngine:
    def execute(self, plan: ir.Table) -> pl.DataFrame:
        """
        Executes the optimized Ibis expression graph.
        Returns a Polars DataFrame.
        """
        return cast(pl.DataFrame, pl.from_arrow(plan.to_pyarrow()))

    def get_storage_size(self, table: ibis.Table) -> int | None:
        """
        Attempts to get the actual storage size from the backend.
        Backend-specific sizing is not implemented.
        """
        return None
