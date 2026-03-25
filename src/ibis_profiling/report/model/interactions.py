import ibis
from typing import Dict, Any, cast


class InteractionEngine:
    """Computes pairwise scatter plot data for numeric variables."""

    @staticmethod
    def compute(
        table: ibis.Table,
        variables: Dict[str, Any],
        row_count: int | None = None,
        sample_size: int = 1000,
        max_interaction_pairs: int = 10,
        correlations: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Calculates pairwise scatter plot coordinates (x, y) for numeric columns.
        Uses a Top-N variables strategy (where N = max_interaction_pairs) for better intuitiveness.
        """
        numeric_cols = [c for c, s in variables.items() if s.get("type") == "Numeric"]
        if len(numeric_cols) < 2:
            return {}

        # 1. Identify "Active" columns based on correlation strength
        # Per user feedback, we treat max_interaction_pairs as the number of VARIABLES to include.
        n_top_cols = max_interaction_pairs
        active_cols = numeric_cols[:n_top_cols]  # Default fallback

        if correlations and "pearson" in correlations:
            pearson = correlations["pearson"]
            p_cols = pearson.get("columns", [])
            p_matrix = pearson.get("matrix", [])

            if p_cols and p_matrix:
                import math

                col_scores = []
                for i, col in enumerate(p_cols):
                    # Score is average absolute correlation with other numeric cols
                    corrs = []
                    for j in range(len(p_cols)):
                        if i != j:
                            val = p_matrix[i][j]
                            # Treat None, NaN, and Inf as 0.0 for scoring purposes
                            if val is None or not math.isfinite(val):
                                corrs.append(0.0)
                            else:
                                corrs.append(abs(val))

                    score = sum(corrs) / len(corrs) if corrs else 0.0
                    col_scores.append((col, score))

                col_scores.sort(key=lambda x: x[1], reverse=True)
                active_cols = [c for c, s in col_scores[:n_top_cols]]

        active_cols = sorted(active_cols)
        from itertools import combinations

        selected_pairs = list(combinations(active_cols, 2))

        # 2. Sample the table if it's large
        if row_count is None:
            try:
                row_count = table.count().to_pyarrow().as_py()
            except Exception:
                row_count = sample_size + 1

        if row_count > sample_size:
            try:
                sampled_table = table.sample(sample_size / row_count)
            except Exception:
                sampled_table = table.limit(sample_size)
        else:
            sampled_table = table

        # 3. Select only active numeric columns
        data_table = sampled_table.select(active_cols)
        data = data_table.to_pyarrow().to_pydict()
        n_points = len(next(iter(data.values()))) if data else 0

        # 4. Build interactions (fully symmetric matrix for active columns)
        interactions = {c: {other: [] for other in active_cols} for c in active_cols}
        for col1, col2 in selected_pairs:
            points = []
            v1_list = data[col1]
            v2_list = data[col2]

            for k in range(n_points):
                v1, v2 = v1_list[k], v2_list[k]
                if v1 is not None and v2 is not None:
                    try:
                        points.append({"x": float(v1), "y": float(v2)})
                    except (TypeError, ValueError):
                        continue

            interactions[col1][col2] = points
            # Symmetrically populate
            interactions[col2][col1] = [{"x": p["y"], "y": p["x"]} for p in points]

        # Self-interactions (identity scatter)
        for c in active_cols:
            points = []
            v_list = data[c]
            for k in range(n_points):
                v = v_list[k]
                if v is not None:
                    try:
                        points.append({"x": float(v), "y": float(v)})
                    except (TypeError, ValueError):
                        continue
            interactions[c][c] = points

        # Add metadata about truncation
        result = cast(Dict[str, Any], interactions)
        result["_metadata"] = {
            "max_pairs": max_interaction_pairs,
            "active_columns": active_cols,
            "total_numeric_columns": len(numeric_cols),
            "is_truncated": len(numeric_cols) > n_top_cols,
        }

        return result
