from typing import Dict, Any
import ibis


class MissingEngine:
    """Computes missing value distributions and patterns following ydata schema."""

    @staticmethod
    def compute(table: ibis.Table, variables: dict) -> Dict[str, Any]:
        """Assembles missing value model from variable statistics and nullity correlations."""
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
            }

        counts = [variables[c].get("n_missing", 0) for c in columns]

        # 1. Missingness Heatmap (Correlation of nullity)
        # We only include columns that have at least some missing values to avoid constant correlation errors
        cols_with_missing = [c for c in columns if variables[c].get("n_missing", 0) > 0]
        heatmap_data = {"columns": [], "matrix": []}

        if len(cols_with_missing) >= 2:
            # Create nullity masks (1 if null, 0 if not)
            from ...metrics import safe_col

            nullity_masks = [
                safe_col(table[c]).isnull().cast("int8").name(c) for c in cols_with_missing
            ]
            mask_table = table.projection(nullity_masks)

            # Use CorrelationEngine's logic for Pearson on the masks
            from .correlations import CorrelationEngine
            import ibis.expr.types as ir

            corr_results = CorrelationEngine._compute_pearson(mask_table, cols_with_missing)

            # We must execute these expressions in a batch
            flat_exprs = []
            for i, row in enumerate(corr_results["matrix"]):
                for j, item in enumerate(row):
                    if isinstance(item, ir.Scalar):
                        flat_exprs.append(item.name(f"mcorr_{i}_{j}"))

            if flat_exprs:
                executed_vals = mask_table.aggregate(flat_exprs).to_pyarrow().to_pydict()
                final_matrix = []
                val_idx = 0
                for i, row in enumerate(corr_results["matrix"]):
                    new_row = []
                    for j, item in enumerate(row):
                        if i == j:
                            new_row.append(1.0)
                        else:
                            key = list(executed_vals.keys())[val_idx]
                            new_row.append(executed_vals[key][0])
                            val_idx += 1
                    final_matrix.append(new_row)
                heatmap_data = {"columns": cols_with_missing, "matrix": final_matrix}

        # 2. Missingness Matrix (Sampled nullity patterns)
        # We sample 250 rows to show the 'location' of missing values
        n_rows = variables[columns[0]].get("n", 1000)
        sample_size = min(250, n_rows)

        # Project nullity masks for the sample
        from ...metrics import safe_col

        sample_masks = [safe_col(table[c]).isnull().name(c) for c in columns]
        # We use limit() for deterministic matrix or sample() for random
        # execute() returns a polars dataframe in our current setup
        sample_df = table.projection(sample_masks).limit(sample_size).execute()

        # Convert to list of lists for JSON
        # We explicitly convert each column to a list to ensure pure JSON arrays
        matrix_data = {
            "columns": columns,
            "values": [sample_df[c].to_list() for c in columns],
        }

        return {
            "bar": {
                "name": "Count",
                "caption": "A simple bar chart of missing values by variable.",
                "matrix": {"columns": columns, "counts": counts},
            },
            "matrix": {
                "name": "Matrix",
                "caption": "A visualization of the locations of missing values (first 250 rows).",
                "matrix": matrix_data,
            },
            "heatmap": {
                "name": "Heatmap",
                "caption": "Pearson correlation of nullity between variables (-1 to 1).",
                "matrix": heatmap_data,
            },
        }
