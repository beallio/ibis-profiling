import polars as pl
from typing import Dict, Any


class SummaryEngine:
    """Handles the transformation of raw Ibis results into the Canonical Variable Model."""

    @staticmethod
    def process_variables(raw_results: pl.DataFrame, schema: dict) -> Dict[str, Any]:
        if raw_results.is_empty():
            return {}

        row = raw_results.row(0, named=True)
        variables = {}

        for col_name, dtype in schema.items():
            dt_str = str(dtype).lower()
            mapped_type = "Categorical"
            if "int" in dt_str or "float" in dt_str:
                mapped_type = "Numeric"
            elif "bool" in dt_str:
                mapped_type = "Boolean"
            elif "time" in dt_str or "date" in dt_str:
                mapped_type = "DateTime"

            # Initialize base model
            variables[col_name] = {
                "type": mapped_type,
                "n_distinct": 0,
                "n_missing": 0,
                "p_missing": 0.0,
            }

        for col, val in row.items():
            if "__" in col and not col.startswith("_dataset__"):
                col_name, metric_name = col.split("__", 1)
                if col_name in variables:
                    # Clean the value (handle numpy/polars types)
                    if hasattr(val, "item"):
                        val = val.item()
                    variables[col_name][metric_name] = val

        return variables
