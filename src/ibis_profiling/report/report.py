import polars as pl
from datetime import datetime, date
import json
import os
import math
from typing import Any
from .model.summary import SummaryEngine
from .model.alerts import AlertEngine
from .structure.report import Report


class ReportEncoder(json.JSONEncoder):
    def default(self, obj):
        import ibis.expr.types as ir

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, ir.Scalar):
            try:
                val = obj.to_pyarrow().as_py()
            except Exception:
                return str(obj)
        else:
            val = obj

        if hasattr(val, "item"):
            val = val.item()

        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
            return val

        return super().default(obj)


class ProfileReport:
    """Canonical Report Model that assembles data from specialized engines."""

    def __init__(self, raw_results: pl.DataFrame, schema: dict):
        self.raw_results = raw_results
        self.schema = schema

        # Core Model Sections
        self.table = {}
        self.variables = {}
        self.correlations = {}
        self.interactions = {}
        self.missing = {}
        self.alerts = []
        self.samples = {}
        self.analysis = {
            "title": "Ibis Profiling Report",
            "date_start": datetime.now().isoformat(),
        }

        self._build()
        self.analysis["date_end"] = datetime.now().isoformat()

    def _to_json_serializable(self, val):
        """Converts Polars/Temporal/Ibis types to standard Python types for JSON serialization."""
        import ibis.expr.types as ir

        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if isinstance(val, ir.Scalar):
            # Convert Ibis scalar to python
            try:
                val = val.to_pyarrow().as_py()
            except Exception:
                return str(val)

        if hasattr(val, "item"):
            val = val.item()

        # Handle NaN/Inf which break strict JSON
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None

        return val

    def _build(self):
        # 1. Variables Summary
        # Temporarily store _dataset if it exists in schema
        dataset_meta = self.schema.pop("_dataset", {})
        self.variables = SummaryEngine.process_variables(self.raw_results, self.schema)

        # 2. Table Summary
        n = 0
        if not self.raw_results.is_empty():
            row = self.raw_results.row(0, named=True)
            n = row.get("_dataset__row_count", 0)

            self.table = {
                "n": n,
                "n_var": len(self.schema),
                "memory_size": self._to_json_serializable(dataset_meta.get("memory_size", 0)),
                "record_size": self._to_json_serializable(dataset_meta.get("record_size", 0)),
                "n_cells_missing": 0,
                "n_vars_with_missing": 0,
                "n_vars_all_missing": 0,
                "types": {},
            }

            # Type counts
            for v in self.variables.values():
                t = v["type"]
                self.table["types"][t] = self.table["types"].get(t, 0) + 1

        # 3. Post-process variables (normalization & derived metrics)
        n_cells_missing = 0
        for col, stats in self.variables.items():
            stats["n"] = n
            # SummaryEngine now uses n_missing, but let's be safe
            m_count = stats.get("n_missing", stats.pop("missing", 0))
            stats["n_missing"] = self._to_json_serializable(m_count)
            stats["p_missing"] = self._to_json_serializable(m_count / n if n > 0 else 0)
            stats["p_distinct"] = self._to_json_serializable(
                stats.get("n_distinct", 0) / n if n > 0 else 0
            )

            stats["count"] = n - m_count
            stats["is_unique"] = stats.get("n_distinct", 0) == n

            n_cells_missing += m_count
            if m_count > 0:
                self.table["n_vars_with_missing"] += 1
            if m_count == n and n > 0:
                self.table["n_vars_all_missing"] += 1

            # Derived Numeric Stats
            if stats.get("type") == "Numeric":
                # Range
                if stats.get("max") is not None and stats.get("min") is not None:
                    stats["range"] = stats["max"] - stats["min"]

                # IQR
                if "75%" in stats and "25%" in stats:
                    stats["iqr"] = stats["75%"] - stats["25%"]

                # CV
                if (
                    stats.get("std") is not None
                    and stats.get("mean") is not None
                    and stats["mean"] != 0
                ):
                    stats["cv"] = stats["std"] / stats["mean"]

                # Zeros Percentage
                if "n_zeros" in stats:
                    stats["p_zeros"] = stats["n_zeros"] / n if n > 0 else 0

                # Infinite Percentage
                if "n_infinite" in stats:
                    stats["p_infinite"] = stats["n_infinite"] / n if n > 0 else 0

                # Negative Percentage
                if "n_negative" in stats:
                    stats["p_negative"] = stats["n_negative"] / n if n > 0 else 0

            # Unique Percentage
            if "n_unique" in stats:
                stats["p_unique"] = stats["n_unique"] / n if n > 0 else 0

            # Ensure other stats are serializable
            for k, v in list(stats.items()):
                stats[k] = self._to_json_serializable(v)

        if self.table:
            self.table["n_cells_missing"] = n_cells_missing
            self.table["p_cells_missing"] = (
                n_cells_missing / (n * self.table["n_var"]) if n > 0 else 0
            )

        # 4. Generate Alerts
        self.alerts = AlertEngine.get_alerts(self.table, self.variables)

    def add_metric(self, col_name: str, metric_name: str, value: any):
        """Adds extra data like samples or histograms to the model."""
        if metric_name in ["head", "tail"]:
            self.samples[metric_name] = value
        elif col_name in self.variables:
            # Handle complex mapping like histograms
            if metric_name == "top_values":
                counts = list(value.get(f"{col_name}_count", []))
                labels = [str(x) for x in value.get(col_name, [])]
                self.variables[col_name]["histogram"] = {"bins": labels, "counts": counts}
            elif metric_name == "length_histogram":
                # Value is a dict with two columns: the length and the count
                keys = list(value.keys())
                # First key is length, second is count
                labels = [str(x) for x in value.get(keys[0], [])]
                counts = list(value.get(keys[1], []))
                self.variables[col_name]["length_histogram"] = {"bins": labels, "counts": counts}
            elif metric_name.startswith("extreme_values_"):
                # Value is a dict like {col_name: [v1, v2, ...]}
                vals = value.get(col_name, [])
                self.variables[col_name][metric_name] = [
                    self._to_json_serializable(x) for x in vals
                ]
            else:
                self.variables[col_name][metric_name] = self._to_json_serializable(value)

    def to_dict(self) -> dict:
        # ydata uses 'auto' as the primary correlation entry
        corrs = self.correlations.copy()
        if "pearson" in corrs and "auto" not in corrs:
            corrs["auto"] = corrs["pearson"]

        d = {
            "analysis": self.analysis,
            "table": self.table,
            "variables": self.variables,
            "correlations": corrs,
            "interactions": self.interactions,
            "missing": self.missing,
            "alerts": self.alerts,
            "sample": self.samples,
            "package": {"name": "ibis-profiling", "version": "0.1.0"},
        }
        # Standardize matrices to list-of-dicts for ydata compatibility
        d = self._format_matrices(d)
        return self._clean_dict(d)

    def _format_matrices(self, obj: Any) -> Any:
        """Recursively transforms {columns, matrix} objects to list-of-dicts."""
        if isinstance(obj, dict):
            if "columns" in obj and "matrix" in obj and isinstance(obj["matrix"], list):
                cols = obj["columns"]
                matrix = obj["matrix"]
                if matrix and isinstance(matrix[0], list):
                    return [dict(zip(cols, row)) for row in matrix]
            return {k: self._format_matrices(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._format_matrices(v) for v in obj]
        return obj

    def _clean_dict(self, obj: Any) -> Any:
        """Recursively replaces NaN/Inf with None for JSON compatibility."""
        if isinstance(obj, dict):
            return {k: self._clean_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_dict(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        return obj

    def get_structure(self) -> Any:
        """Returns the logical structure of the report."""
        return Report(self.to_dict()).get_structure()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, cls=ReportEncoder)

    def to_file(self, output_file: str):
        content = self.to_json() if output_file.endswith(".json") else self.to_html()
        with open(output_file, "w") as f:
            f.write(content)

    def to_html(self) -> str:
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "spa.html")
        with open(template_path, "r") as f:
            html = f.read()
        # Minify JSON for embedding
        report_json = json.dumps(self.to_dict(), separators=(",", ":"), cls=ReportEncoder)
        return html.replace("{{REPORT_DATA}}", report_json)

    def get_description(self) -> dict:
        return self.to_dict()
