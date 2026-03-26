from typing import Dict, Any
import ibis
import math


class MissingEngine:
    """Computes missing value distributions and patterns following ydata schema."""

    @staticmethod
    def compute(
        table: ibis.Table,
        variables: dict,
        max_heatmap_columns: int = 15,
        max_matrix_columns: int = 50,
    ) -> Dict[str, Any]:
        """Assembles missing value model from variable statistics and nullity correlations."""
        import ibis.expr.types as ir
        import ibis.expr.datatypes as dt

        warnings = []

        columns = list(variables.keys())
        if not columns:
            return {
                "bar": {
                    "name": "Count",
                    "caption": "A simple bar chart of missing values by variable.",
                    "matrix": {"columns": [], "counts": []},
                },
                "matrix": {
                    "name": "Matrix",
                    "caption": "A visualization of the locations of missing values (first 250 rows).",
                    "matrix": {"columns": [], "values": []},
                },
                "heatmap": {
                    "name": "Heatmap",
                    "caption": "Pearson correlation of nullity between variables (-1 to 1).",
                    "matrix": {"columns": [], "matrix": []},
                },
                "warnings": [],
            }

        counts = [variables[c].get("n_missing", 0) for c in columns]

        # 1. Missingness Heatmap (Correlation of nullity)
        # We only include columns that have at least some missing values to avoid constant correlation errors
        cols_with_missing = [c for c in columns if variables[c].get("n_missing", 0) > 0]
        heatmap_data = {"columns": [], "matrix": []}

        # Truncate if necessary to avoid O(n^2) blowups
        original_missing_count = len(cols_with_missing)
        is_heatmap_truncated = False
        h_limit = max(2, max_heatmap_columns)

        if original_missing_count > h_limit:
            is_heatmap_truncated = True
            # Prioritize columns with MOST missing values
            cols_with_missing = sorted(
                cols_with_missing, key=lambda c: variables[c].get("n_missing", 0), reverse=True
            )[:h_limit]

        if len(cols_with_missing) >= 2:
            # Create nullity masks (1 if null, 0 if not)
            from ...metrics import safe_col

            nullity_masks = [
                safe_col(table[c]).isnull().cast(dt.Int8).name(c) for c in cols_with_missing
            ]
            mask_table = table.projection(nullity_masks)

            # Use CorrelationEngine's logic for Pearson on the masks
            from .correlations import CorrelationEngine

            corr_results = CorrelationEngine._compute_pearson(mask_table, cols_with_missing)

            # Execute these expressions
            flat_exprs = []
            for i, row in enumerate(corr_results["matrix"]):
                for j, item in enumerate(row):
                    if isinstance(item, ir.Scalar):
                        flat_exprs.append(item.name(f"mcorr_{i}_{j}"))

            if flat_exprs:
                res = mask_table.aggregate(flat_exprs).to_pyarrow().to_pydict()
                final_matrix = [[1.0 for _ in cols_with_missing] for _ in cols_with_missing]
                non_finite_count = 0
                for i in range(len(cols_with_missing)):
                    for j in range(len(cols_with_missing)):
                        if i != j:
                            key = f"mcorr_{i}_{j}"
                            val = res[key][0]
                            # Handle potential NaNs/Infs from zero-variance masks
                            # Coerce to float to avoid TypeError on non-float numeric types (e.g. Decimal)
                            is_f = False
                            try:
                                if val is not None and math.isfinite(float(val)):
                                    is_f = True
                            except (TypeError, ValueError):
                                pass

                            if is_f:
                                final_matrix[i][j] = float(val)
                            else:
                                final_matrix[i][j] = 0.0
                                non_finite_count += 1

                if non_finite_count > 0:
                    warnings.append(
                        f"Missingness heatmap contains {non_finite_count} undefined (NaN/Inf) "
                        "correlation pairs (likely due to columns with 0% or 100% missing values)."
                    )
                heatmap_data = {"columns": cols_with_missing, "matrix": final_matrix}

        # 2. Missingness Matrix (Sampled nullity patterns)
        # We sample 250 rows to show the 'location' of missing values
        n_rows = variables[columns[0]].get("n", 1000)
        sample_size = min(250, n_rows)

        # Truncate matrix columns if necessary
        original_matrix_count = len(columns)
        is_matrix_truncated = False
        m_limit = max(2, max_matrix_columns)
        matrix_cols = columns

        if original_matrix_count > m_limit:
            is_matrix_truncated = True
            # Prioritize columns with ANY missing values, then by count
            matrix_cols = sorted(
                columns, key=lambda c: variables[c].get("n_missing", 0), reverse=True
            )[:m_limit]

        # Project nullity masks for the sample
        from ...metrics import safe_col

        sample_masks = [safe_col(table[c]).isnull().name(c) for c in matrix_cols]
        # We use limit() for deterministic matrix or sample() for random
        # to_pyarrow() returns a pyarrow Table, which is backend-agnostic
        sample_table = table.projection(sample_masks).limit(sample_size).to_pyarrow()

        # Convert to list of lists for JSON
        # Template expects matrix: { columns: [], matrix: [row1, row2, ...] }
        # where row is [True, False, ...]
        # We iterate over rows from pyarrow to get a consistent list of lists
        matrix_values = [[row[c] for c in matrix_cols] for row in sample_table.to_pylist()]

        return {
            "bar": {
                "name": "Count",
                "caption": "A simple bar chart of missing values by variable.",
                # Special case: 'counts' is used instead of 'matrix' for the bar chart
                # format_matrices won't touch this as it doesn't have a 'matrix' key
                "matrix": {"columns": columns, "counts": counts},
            },
            "matrix": {
                "name": "Matrix",
                "caption": "A visualization of the locations of missing values (first 250 rows).",
                "matrix": {
                    "columns": matrix_cols,
                    "matrix": matrix_values,
                    "sampled": n_rows > sample_size,
                    "sample_size": sample_size,
                    "_metadata": {
                        "truncated": is_matrix_truncated,
                        "original_count": original_matrix_count,
                        "limit": m_limit,
                    },
                },
            },
            "heatmap": {
                "name": "Heatmap",
                "caption": "Pearson correlation of nullity between variables (-1 to 1).",
                "matrix": {
                    "columns": heatmap_data["columns"],
                    "matrix": heatmap_data["matrix"],
                    "sampled": False,
                    "_metadata": {
                        "truncated": is_heatmap_truncated,
                        "original_count": original_missing_count,
                        "limit": h_limit,
                    },
                },
            },
            "warnings": warnings,
        }
