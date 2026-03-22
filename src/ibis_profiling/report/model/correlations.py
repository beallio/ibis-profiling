import ibis
from typing import List, Dict, Any


class CorrelationEngine:
    """Computes pairwise correlations using Ibis backends."""

    @staticmethod
    def compute_all(table: ibis.Table, variables: dict) -> Dict[str, Any]:
        """Calculates all supported correlation matrices."""
        import ibis.expr.types as ir
        import ibis.expr.datatypes as dt

        schema = table.schema()
        # Use schema as source of truth for "Numeric" suitability
        numeric_cols = [c for c, t in schema.items() if isinstance(t, (dt.Numeric, dt.Boolean))]

        if len(numeric_cols) < 2:
            return {
                "pearson": {"columns": numeric_cols, "matrix": []},
                "spearman": {"columns": numeric_cols, "matrix": []},
            }

        # Limit Spearman on very large datasets to avoid performance collapse
        row_count = table.count().to_pyarrow().as_py()
        SPEARMAN_THRESHOLD = 1_000_000

        # 1. Pearson Pass
        pearson_meta = CorrelationEngine._compute_pearson(table, numeric_cols)
        flat_pearson = []
        for i, row in enumerate(pearson_meta["matrix"]):
            for j, item in enumerate(row):
                if isinstance(item, ir.Scalar):
                    flat_pearson.append(item.name(f"p_{i}_{j}"))

        if flat_pearson:
            res = table.aggregate(flat_pearson).to_pyarrow().to_pydict()
            final_pearson = [[1.0 for _ in numeric_cols] for _ in numeric_cols]
            for i in range(len(numeric_cols)):
                for j in range(len(numeric_cols)):
                    if i != j:
                        key = f"p_{i}_{j}"
                        final_pearson[i][j] = res[key][0]
            pearson = {"columns": numeric_cols, "matrix": final_pearson}
        else:
            pearson = {"columns": numeric_cols, "matrix": []}

        # 2. Spearman Pass
        spearman = {"columns": numeric_cols, "matrix": []}
        if row_count <= SPEARMAN_THRESHOLD:
            spearman_meta = CorrelationEngine._compute_spearman(table, numeric_cols)
            rank_exprs = [spearman_meta["rank_exprs"][c].name(f"rank_{c}") for c in numeric_cols]
            rank_table = table.mutate(*rank_exprs)

            flat_spearman = []
            for i, c1 in enumerate(numeric_cols):
                for j, c2 in enumerate(numeric_cols):
                    if i < j:
                        r1 = rank_table[f"rank_{c1}"]
                        r2 = rank_table[f"rank_{c2}"]
                        # Pearson on Ranks
                        expr = r1.cov(r2, how="pop") / (r1.std(how="pop") * r2.std(how="pop"))
                        flat_spearman.append(expr.name(f"s_{i}_{j}"))

            if flat_spearman:
                res = rank_table.aggregate(flat_spearman).to_pyarrow().to_pydict()
                final_spearman = [[1.0 for _ in numeric_cols] for _ in numeric_cols]
                for i in range(len(numeric_cols)):
                    for j in range(len(numeric_cols)):
                        if i < j:
                            key = f"s_{i}_{j}"
                            val = res[key][0]
                            final_spearman[i][j] = val
                            final_spearman[j][i] = val
                spearman = {"columns": numeric_cols, "matrix": final_spearman}

        return {
            "pearson": pearson,
            "spearman": spearman,
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
        import ibis.expr.datatypes as dt

        matrix = []
        for i, c1 in enumerate(cols):
            row = []
            for j, c2 in enumerate(cols):
                if i == j:
                    row.append(1.0)
                else:
                    # Pearson Correlation Expression (Manual to handle NaNs)
                    # corr(x, y) = cov(x, y) / (std(x) * std(y))
                    s1 = safe_col(table[c1]).cast(dt.Float64)
                    s2 = safe_col(table[c2]).cast(dt.Float64)
                    expr = s1.cov(s2, how="pop") / (s1.std(how="pop") * s2.std(how="pop"))
                    row.append(expr)
            matrix.append(row)

        return {"columns": cols, "matrix": matrix}
