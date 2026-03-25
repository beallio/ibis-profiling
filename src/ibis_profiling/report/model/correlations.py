import ibis
from typing import List, Dict, Any


class CorrelationEngine:
    """Computes pairwise correlations using Ibis backends."""

    @staticmethod
    def compute_all(
        table: ibis.Table,
        variables: dict,
        row_count: int | None = None,
        sampling_threshold: int = 1_000_000,
        sample_size: int = 1_000_000,
        max_columns: int = 15,
    ) -> Dict[str, Any]:
        """Calculates all supported correlation matrices with sampling for large datasets."""
        import ibis.expr.types as ir
        import ibis.expr.datatypes as dt

        schema = table.schema()
        # Use schema as source of truth for "Numeric" suitability
        numeric_cols = [c for c, t in schema.items() if isinstance(t, (dt.Numeric, dt.Boolean))]

        # Truncate if necessary to avoid O(n^2) blowups
        # Enforce minimum of 2 columns for a matrix, otherwise return empty
        max_columns = max(2, max_columns)
        original_count = len(numeric_cols)
        is_truncated = False
        if original_count > max_columns:
            is_truncated = True

            # Deterministic Selection: Top by missingness (ASC) and variance (DESC)
            def sort_key(c):
                stats = variables.get(c, {})
                # Coerce to safe numeric defaults before sorting
                try:
                    n_missing = float(stats.get("n_missing", 0) or 0)
                except (TypeError, ValueError):
                    n_missing = 0.0

                try:
                    # Negate variance for descending sort
                    variance = -float(stats.get("variance", 0) or 0)
                except (TypeError, ValueError):
                    variance = 0.0

                return (n_missing, variance, c)

            numeric_cols = sorted(numeric_cols, key=sort_key)[:max_columns]

        if len(numeric_cols) < 2:
            return {
                "pearson": {"columns": numeric_cols, "matrix": [], "sampled": False},
                "spearman": {"columns": numeric_cols, "matrix": [], "sampled": False},
                "_metadata": {
                    "truncated": is_truncated,
                    "original_count": original_count,
                    "limit": max_columns,
                },
            }

        # Robust row count detection for sampling
        if row_count is None:
            row_count = variables.get("_dataset", {}).get("n")

        if row_count is None:
            # Try to find 'n' in any variable entry
            for stats in variables.values():
                if isinstance(stats, dict) and "n" in stats:
                    row_count = stats["n"]
                    break

        if row_count is None:
            row_count = table.count().to_pyarrow().as_py()

        is_sampled = row_count > sampling_threshold
        calc_table = table
        if is_sampled:
            try:
                calc_table = table.sample(sample_size / row_count)
            except Exception:
                calc_table = table.limit(sample_size)

        # 1. Pearson Pass
        pearson_meta = CorrelationEngine._compute_pearson(calc_table, numeric_cols)
        flat_pearson = []
        for i, row in enumerate(pearson_meta["matrix"]):
            for j, item in enumerate(row):
                if isinstance(item, ir.Scalar):
                    flat_pearson.append(item.name(f"p_{i}_{j}"))

        if flat_pearson:
            res = calc_table.aggregate(flat_pearson).to_pyarrow().to_pydict()
            final_pearson = [[1.0 for _ in numeric_cols] for _ in numeric_cols]
            for i in range(len(numeric_cols)):
                for j in range(len(numeric_cols)):
                    if i != j:
                        key = f"p_{i}_{j}"
                        val = res[key][0]
                        final_pearson[i][j] = val
            pearson = {
                "columns": numeric_cols,
                "matrix": final_pearson,
                "sampled": is_sampled,
                "sample_size": sample_size if is_sampled else None,
            }
        else:
            pearson = {
                "columns": numeric_cols,
                "matrix": [],
                "sampled": is_sampled,
                "sample_size": sample_size if is_sampled else None,
            }

        # 2. Spearman Pass
        spearman_meta = CorrelationEngine._compute_spearman(calc_table, numeric_cols)
        rank_exprs = [spearman_meta["rank_exprs"][c].name(f"rank_{c}") for c in numeric_cols]
        rank_table = calc_table.mutate(*rank_exprs)

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
            spearman = {
                "columns": numeric_cols,
                "matrix": final_spearman,
                "sampled": is_sampled,
                "sample_size": sample_size if is_sampled else None,
            }
        else:
            spearman = {
                "columns": numeric_cols,
                "matrix": [],
                "sampled": is_sampled,
                "sample_size": sample_size if is_sampled else None,
            }

        return {
            "pearson": pearson,
            "spearman": spearman,
            "_metadata": {
                "truncated": is_truncated,
                "original_count": original_count,
                "limit": max_columns,
            },
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
