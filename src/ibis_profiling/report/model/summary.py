import polars as pl
from typing import Dict, Any


class SummaryEngine:
    """Handles the transformation of raw Ibis results into the Canonical Variable Model."""

    @staticmethod
    def process_variables(raw_results: pl.DataFrame, schema: dict) -> Dict[str, Any]:
        import ibis.expr.datatypes as dt

        variables = {}

        for col_name, dtype in schema.items():
            if col_name == "_dataset":
                continue
            # Use Ibis DataType hierarchy for robust classification
            if isinstance(dtype, dt.Numeric):
                mapped_type = "Numeric"
            elif isinstance(dtype, dt.Boolean):
                mapped_type = "Boolean"
            elif isinstance(dtype, (dt.Date, dt.Time, dt.Timestamp)):
                mapped_type = "DateTime"
            elif isinstance(dtype, dt.String):
                mapped_type = "Categorical"
            elif isinstance(dtype, (dt.Array, dt.Map, dt.Struct, dt.JSON)):
                mapped_type = "Unsupported"
            else:
                # Default to Unsupported for unknown/complex types
                mapped_type = "Unsupported"

            # Initialize base model
            variables[col_name] = {
                "type": mapped_type,
                "n_distinct": 0,
                "n_unique": 0,
                "n_missing": 0,
                "p_missing": 0.0,
                "n": 0,
                "count": 0,
            }

        if raw_results.is_empty():
            return variables

        row = raw_results.row(0, named=True)

        for col, val in row.items():
            if "__" in col and not col.startswith("_dataset__"):
                col_name, metric_name = col.rsplit("__", 1)
                if col_name in variables:
                    # Clean the value
                    if hasattr(val, "item"):
                        val = val.item()

                    # Mapping logic to match ydata JSON schema
                    if metric_name.startswith("p") and metric_name[1:].isdigit():
                        p_key = metric_name[1:] + "%"
                        variables[col_name][p_key] = val
                    elif metric_name == "missing":
                        variables[col_name]["n_missing"] = val
                    elif metric_name == "zeros":
                        variables[col_name]["n_zeros"] = val
                    elif metric_name == "infinite":
                        variables[col_name]["n_infinite"] = val
                    elif metric_name == "n_zeros":
                        variables[col_name]["n_zeros"] = val
                    elif metric_name == "n_missing":
                        variables[col_name]["n_missing"] = val
                    elif metric_name == "n_infinite":
                        variables[col_name]["n_infinite"] = val
                    elif metric_name == "median":
                        variables[col_name]["50%"] = val
                    elif metric_name == "n_negative":
                        variables[col_name]["n_negative"] = val
                    else:
                        variables[col_name][metric_name] = val

        return variables
