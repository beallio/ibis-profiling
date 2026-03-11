import polars as pl
from datetime import datetime, date
import json
import os


class ProfileReport:
    def __init__(self, raw_results: pl.DataFrame, schema: dict):
        self.raw_results = raw_results
        self.schema = schema
        self.dataset_stats = {}
        self.column_stats = {}
        self.samples = {}
        self._build()

    def _to_json_serializable(self, val):
        """Converts Polars/Temporal types to standard Python types for JSON serialization."""
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if hasattr(val, "item"):
            return val.item()
        return val

    def _build(self):
        if self.raw_results.is_empty():
            return

        row = self.raw_results.row(0, named=True)

        n_var = len(self.schema)
        self.dataset_stats["n_var"] = n_var

        for col_name, dtype in self.schema.items():
            dt_str = str(dtype)
            if "int" in dt_str.lower() or "float" in dt_str.lower():
                mapped_type = "Numeric"
            elif "bool" in dt_str.lower():
                mapped_type = "Boolean"
            elif "time" in dt_str.lower() or "date" in dt_str.lower():
                mapped_type = "DateTime"
            else:
                mapped_type = "Categorical"

            self.column_stats[col_name] = {"type": mapped_type}

        for col, val in row.items():
            val = self._to_json_serializable(val)
            if col.startswith("_dataset__"):
                metric_name = col.replace("_dataset__", "", 1)
                self.dataset_stats[metric_name] = val
            elif "__" in col:
                col_name, metric_name = col.split("__", 1)
                if col_name in self.column_stats:
                    self.column_stats[col_name][metric_name] = val

        # Calculate derived dataset metrics
        n = self.dataset_stats.get("row_count", 0)
        n_cells = n * n_var
        self.dataset_stats["n"] = n
        self.dataset_stats["n_cells"] = n_cells

        missing_cells = sum(stats.get("missing", 0) for stats in self.column_stats.values())
        self.dataset_stats["n_cells_missing"] = missing_cells
        self.dataset_stats["p_cells_missing"] = missing_cells / n_cells if n_cells > 0 else 0

        type_counts = {}
        for stats in self.column_stats.values():
            t = stats["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        self.dataset_stats["types"] = type_counts

        # Format variables to match SPA schema
        for col, stats in self.column_stats.items():
            stats["n_distinct"] = stats.get("n_distinct", 0)
            stats["n_missing"] = stats.get("missing", 0)
            stats["p_missing"] = stats["n_missing"] / n if n > 0 else 0

            # Re-map histograms
            if "top_values" in stats:
                tv = stats.pop("top_values")
                labels = [str(x) for x in tv.get(col, [])]
                counts = list(tv.get(f"{col}_count", []))
                stats["histogram"] = {"bins": labels, "counts": counts}

    def add_metric(self, col_name: str, metric_name: str, value: any):
        """Manually adds a metric result to the report."""
        if metric_name in ["head", "tail"]:
            self.samples[metric_name] = value
            return

        val = self._to_json_serializable(value)
        if col_name == "_dataset":
            self.dataset_stats[metric_name] = val
        else:
            if col_name not in self.column_stats:
                self.column_stats[col_name] = {}
            self.column_stats[col_name][metric_name] = val

    def get_alerts(self):
        alerts = []
        n = self.dataset_stats.get("n", 1)
        for col, stats in self.column_stats.items():
            if stats.get("n_distinct") == n and n > 0:
                alerts.append({"type": "UNIQUE", "fields": [col]})
            if stats.get("n_missing", 0) > 0:
                alerts.append({"type": "MISSING", "fields": [col]})
            if stats.get("zeros", 0) > 0:
                alerts.append({"type": "ZEROS", "fields": [col]})
        return alerts

    def to_dict(self):
        return {
            "table": self.dataset_stats,
            "variables": self.column_stats,
            "correlations": {},
            "interactions": {},
            "missing": {},
            "alerts": self.get_alerts(),
            "sample": self.samples,
            "package": {"name": "ibis-profiling", "version": "0.1.0"},
        }

    def get_description(self) -> dict:
        """Alias for to_dict() to match ydata-profiling API."""
        return self.to_dict()

    def to_json(self) -> str:
        """Returns the report as a JSON string."""

        class ReportEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                if hasattr(obj, "item"):
                    return obj.item()
                return super().default(obj)

        return json.dumps(self.to_dict(), indent=2, cls=ReportEncoder)

    def to_file(self, output_file: str):
        """Writes the report to a file (HTML or JSON)."""
        content = ""
        if output_file.endswith(".json"):
            content = self.to_json()
        else:
            content = self.to_html()

        with open(output_file, "w") as f:
            f.write(content)

    def to_html(self, template: str = "ydata") -> str:
        """Generates the HTML report using the SPA template."""
        # Load the SPA template
        template_path = os.path.join(os.path.dirname(__file__), "templates", "spa.html")
        with open(template_path, "r") as f:
            html = f.read()

        json_data = self.to_json()
        html = html.replace("{{REPORT_DATA}}", json_data)

        return html
