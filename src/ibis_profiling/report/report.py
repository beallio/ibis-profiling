import polars as pl
from datetime import datetime, date
import json
import os
from typing import Any
from .model.summary import SummaryEngine
from .model.alerts import AlertEngine
from .structure.report import Report


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

        self._build()

    def _to_json_serializable(self, val):
        """Converts Polars/Temporal types to standard Python types for JSON serialization."""
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if hasattr(val, "item"):
            return val.item()
        return val

    def _build(self):
        # 1. Variables Summary
        self.variables = SummaryEngine.process_variables(self.raw_results, self.schema)

        # 2. Table Summary
        n = 0
        if not self.raw_results.is_empty():
            row = self.raw_results.row(0, named=True)
            n = row.get("_dataset__row_count", 0)
            self.table = {
                "n": n,
                "n_var": len(self.schema),
                "n_cells_missing": sum(v.get("missing", 0) for v in self.variables.values()),
                "types": {},
            }
            self.table["p_cells_missing"] = (
                self.table["n_cells_missing"] / (n * self.table["n_var"]) if n > 0 else 0
            )

            # Type counts
            for v in self.variables.values():
                t = v["type"]
                self.table["types"][t] = self.table["types"].get(t, 0) + 1

        # 3. Post-process variables (normalization)
        for col, stats in self.variables.items():
            stats["n_missing"] = self._to_json_serializable(stats.pop("missing", 0))
            stats["p_missing"] = self._to_json_serializable(stats["n_missing"] / n if n > 0 else 0)
            stats["distinct_perc"] = self._to_json_serializable(
                stats.get("n_distinct", 0) / n if n > 0 else 0
            )

            # Ensure other stats are serializable
            for k, v in list(stats.items()):
                stats[k] = self._to_json_serializable(v)

        # 4. Generate Alerts
        self.alerts = AlertEngine.get_alerts(self.table, self.variables)

        # 5. Generate Missing Values summary
        from .model.missing import MissingEngine

        self.missing = MissingEngine.process(self.variables)

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
            else:
                self.variables[col_name][metric_name] = self._to_json_serializable(value)

    def to_dict(self) -> dict:
        return {
            "table": self.table,
            "variables": self.variables,
            "correlations": self.correlations,
            "interactions": self.interactions,
            "missing": self.missing,
            "alerts": self.alerts,
            "sample": self.samples,
            "package": {"name": "ibis-profiling", "version": "0.1.0"},
        }

    def get_structure(self) -> Any:
        """Returns the logical structure of the report."""
        return Report(self.to_dict()).get_structure()

    def to_json(self) -> str:
        class ReportEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                if hasattr(obj, "item"):
                    return obj.item()
                return super().default(obj)

        return json.dumps(self.to_dict(), indent=2, cls=ReportEncoder)

    def to_file(self, output_file: str):
        content = self.to_json() if output_file.endswith(".json") else self.to_html()
        with open(output_file, "w") as f:
            f.write(content)

    def to_html(self) -> str:
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "spa.html")
        with open(template_path, "r") as f:
            html = f.read()
        return html.replace("{{REPORT_DATA}}", self.to_json())

    def get_description(self) -> dict:
        return self.to_dict()
