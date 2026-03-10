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
