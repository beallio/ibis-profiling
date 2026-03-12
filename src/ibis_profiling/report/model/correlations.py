import ibis
from typing import List, Dict, Any


class CorrelationEngine:
    """Computes pairwise correlations using Ibis backends."""

    @staticmethod
    def compute_all(table: ibis.Table, variables: dict) -> Dict[str, Any]:
        """Calculates all supported correlation matrices."""
        numeric_cols = [c for c, s in variables.items() if s.get("type") == "Numeric"]

        pearson = CorrelationEngine._compute_pearson(table, numeric_cols)
        spearman = CorrelationEngine._compute_spearman(table, numeric_cols)

        return {
            "auto": pearson,  # ydata often uses 'auto'
            "pearson": pearson,
            "spearman": spearman,
            # placeholders for others
            "kendall": {"columns": [], "matrix": []},
            "phi_k": {"columns": [], "matrix": []},
            "cramers": {"columns": [], "matrix": []},
        }

    @staticmethod
    def _compute_spearman(table: ibis.Table, cols: List[str]) -> Dict[str, Any]:
        if len(cols) < 2:
            return {"columns": cols, "matrix": []}

        # We cannot nest RANK() inside COVAR_POP() in DuckDB.
        # We must return expressions that represent the ranks.
        # The caller will create a CTE/temp table with these ranks.

        ranks = {}
        for c in cols:
            # We must use a window for rank()
            # If no order is provided, it ranks based on the column itself
            ranks[c] = table[c].rank()

        # To maintain the same structure as _compute_pearson, we return a matrix
        # but the items are now placeholders that the caller will handle
        # by executing on a RANK-transformed table.
        matrix = []
        for i, c1 in enumerate(cols):
            row = []
            for j, c2 in enumerate(cols):
                if i == j:
                    row.append(1.0)
                else:
                    # Placeholder for the rank-based Pearson
                    row.append(f"spearman_{i}_{j}")
            matrix.append(row)

        return {"columns": cols, "matrix": matrix, "rank_exprs": ranks}

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
