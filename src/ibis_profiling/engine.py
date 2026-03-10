import ibis
import pandas as pd


class ExecutionEngine:
    def execute(self, plan: ibis.expr.types.Table) -> pd.DataFrame:
        """
        Executes the optimized Ibis expression graph.
        All computation is pushed down to the backend engine here.
        """
        return plan.execute()
