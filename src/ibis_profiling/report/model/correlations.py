import ibis
from typing import List, Dict, Any


class CorrelationEngine:
    """Computes pairwise correlations using Ibis backends."""

    @staticmethod
    def compute_all(table: ibis.Table, variables: dict) -> Dict[str, Any]:
        """Calculates all supported correlation matrices."""
        numeric_cols = [c for c, s in variables.items() if s.get("type") == "Numeric"]

        pearson = CorrelationEngine._compute_pearson(table, numeric_cols)

        return {
            "auto": pearson,  # ydata often uses 'auto'
            "pearson": pearson,
            # placeholders for others
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
        # We manually compute pearson to avoid DuckDB NaN -> OutOfRange error in corr()
        from ...metrics import safe_col

        matrix = []
        for i, c1 in enumerate(cols):
            row = []
            for j, c2 in enumerate(cols):
                if i == j:
                    row.append(1.0)
                else:
                    # Pearson Correlation Expression (Manual to handle NaNs)
                    # corr(x, y) = cov(x, y) / (std(x) * std(y))
                    s1 = safe_col(table[c1])
                    s2 = safe_col(table[c2])
                    expr = s1.cov(s2, how="pop") / (s1.std(how="pop") * s2.std(how="pop"))
                    row.append(expr)
            matrix.append(row)

        return {"columns": cols, "matrix": matrix}
