import ibis
import polars as pl


class ExecutionEngine:
    def execute(self, plan: ibis.expr.types.Table) -> pl.DataFrame:
        """
        Executes the optimized Ibis expression graph.
        Returns a Polars DataFrame.
        Computation is pushed down to the backend engine.
        """
        return pl.from_arrow(plan.to_pyarrow())

    def get_storage_size(self, table: ibis.Table) -> int | None:
        """
        Attempts to get the actual storage size from the backend.
        Currently supports: DuckDB.
        """
        try:
            con = table._find_backend()
        except Exception:
            return None

        # Check if it's DuckDB
        if hasattr(con, "con") and hasattr(con, "name") and con.name == "duckdb":
            try:
                # DuckDB storage info only works on base tables
                # If it's a view or expression, we'll get an error
                # We try to find the base table name if possible
                if isinstance(table.op(), ibis.expr.operations.relations.UnboundTable):
                    table_name = table.op().name
                elif isinstance(table.op(), ibis.expr.operations.relations.DatabaseTable):
                    table_name = table.op().name
                else:
                    return None

                res = con.con.execute(f"CALL pragma_storage_info('{table_name}')").pl()
                # Sum the segment sizes (estimated)
                if not res.is_empty():
                    # Segment sizes in DuckDB blocks
                    # This is a very rough estimate of 'size on disk' vs 'memory footprint'
                    return res["estimated_size"].sum()
            except Exception:
                return None

        return None
