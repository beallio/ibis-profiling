import ibis
from typing import Dict, List, Any


class InteractionEngine:
    """Computes pairwise scatter plot data for numeric variables."""

    @staticmethod
    def compute(
        table: ibis.Table, variables: Dict[str, Any], sample_size: int = 1000
    ) -> Dict[str, Dict[str, List[Dict[str, float]]]]:
        """
        Calculates pairwise scatter plot coordinates (x, y) for numeric columns.
        Uses sampling for efficiency on large datasets.
        """
        numeric_cols = [c for c, s in variables.items() if s.get("type") == "Numeric"]
        if len(numeric_cols) < 2:
            return {}

        # 1. Sample the table if it's large
        # We need to ensure we have actual values, so we filter out nulls for the pair if possible
        # but a global sample is easier and usually sufficient.
        row_count = table.count().to_pyarrow().as_py()

        if row_count > sample_size:
            # ibis.Table.sample() is not supported by all backends equally
            # (e.g. DuckDB supports it, but some others might not)
            # A more robust way is to use limit if the backend doesn't support sampling
            try:
                sampled_table = table.sample(sample_size / row_count)
            except Exception:
                sampled_table = table.limit(sample_size)
        else:
            sampled_table = table

        # 2. Select only numeric columns to minimize data transfer
        data_table = sampled_table.select(numeric_cols)

        # 3. Execute and convert to a list of dicts for easy access
        # Using Polars or PyArrow for fast conversion
        data = data_table.to_pyarrow().to_pydict()
        n_points = len(next(iter(data.values()))) if data else 0

        # 4. Build the nested interactions structure
        interactions = {}
        for i, col1 in enumerate(numeric_cols):
            interactions[col1] = {}
            for j, col2 in enumerate(numeric_cols):
                if i == j:
                    continue

                # Extract (x, y) pairs, skipping nulls for this specific pair
                points = []
                v1_list = data[col1]
                v2_list = data[col2]

                for k in range(n_points):
                    v1 = v1_list[k]
                    v2 = v2_list[k]
                    if v1 is not None and v2 is not None:
                        # Ensure we have python floats for JSON
                        try:
                            points.append({"x": float(v1), "y": float(v2)})
                        except (TypeError, ValueError):
                            continue

                interactions[col1][col2] = points

        return interactions
