import ibis
from typing import List, Dict, Any


class CorrelationEngine:
    """Computes pairwise correlations using Ibis backends."""

    @staticmethod
    def compute_all(table: ibis.Table, variables: dict) -> Dict[str, Any]:
        """Calculates all supported correlation matrices."""
        numeric_cols = [c for c, s in variables.items() if s.get("type") == "Numeric"]

        return {
            "pearson": CorrelationEngine._compute_pearson(table, numeric_cols),
            # placeholders for others to match ydata spec
            "spearman": {"columns": [], "matrix": []},
            "kendall": {"columns": [], "matrix": []},
            "phi_k": {"columns": [], "matrix": []},
            "cramers": {"columns": [], "matrix": []},
        }

    @staticmethod
    def _compute_pearson(table: ibis.Table, cols: List[str]) -> Dict[str, Any]:
        if len(cols) < 2:
            return {"columns": cols, "matrix": []}

        # For 20M rows, we compute the matrix efficiently
        # Ibis doesn't have a native 'corr_matrix', so we build expressions
        matrix = []
        for i, c1 in enumerate(cols):
            row = []
            for j, c2 in enumerate(cols):
                if i == j:
                    row.append(1.0)
                else:
                    # Pearson Correlation Expression
                    expr = ibis.expr.api.corr(table[c1], table[c2])
                    row.append(expr)
            matrix.append(row)

        # Execution is handled by the main engine to batch these,
        # but for this logic, we return the structure.
        return {"columns": cols, "matrix": matrix}
