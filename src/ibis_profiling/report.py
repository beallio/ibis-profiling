import polars as pl
from datetime import datetime, date


class ProfileReport:
    def __init__(self, raw_results: pl.DataFrame, schema: dict):
        self.raw_results = raw_results
        self.schema = schema
        self.dataset_stats = {}
        self.column_stats = {}
        self._build()

    def _to_json_serializable(self, val):
        """Converts Polars/Temporal types to standard Python types for JSON serialization."""
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        return val

    def _build(self):
        if self.raw_results.is_empty():
            return

        # Get the first row as a dictionary
        row = self.raw_results.row(0, named=True)

        n_var = len(self.schema)
        self.dataset_stats["n_var"] = n_var

        for col_name, dtype in self.schema.items():
            self.column_stats[col_name] = {"type": str(dtype)}

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
        self.dataset_stats["n_cells"] = n_cells

        missing_cells = sum(stats.get("missing", 0) for stats in self.column_stats.values())
        self.dataset_stats["missing_cells"] = missing_cells
        self.dataset_stats["missing_cells_perc"] = missing_cells / n_cells if n_cells > 0 else 0

        # Calculate derived column metrics (variance, range, etc.)
        for col, stats in self.column_stats.items():
            if (
                "max" in stats
                and "min" in stats
                and isinstance(stats["max"], (int, float))
                and isinstance(stats["min"], (int, float))
            ):
                stats["range"] = stats["max"] - stats["min"]

            if stats.get("std") is not None:
                stats["variance"] = stats["std"] ** 2
                if stats.get("mean") and stats["mean"] != 0:
                    stats["cv"] = stats["std"] / stats["mean"]

            if n > 0 and "unique" in stats:
                stats["distinct_perc"] = stats["unique"] / n

    def to_dict(self):
        return {"dataset": self.dataset_stats, "columns": self.column_stats}

    def to_html(self) -> str:
        """Generates a simple HTML report for the profile."""
        html = [
            "<html><head><title>Ibis Profiling Report</title>",
            "<style>body { font-family: sans-serif; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; } h1, h2 { color: #333; }</style>",
            "</head><body>",
            "<h1>Data Profile Report</h1>",
            "<h2>Dataset Statistics</h2>",
            "<table><tr><th>Metric</th><th>Value</th></tr>",
        ]

        for k, v in self.dataset_stats.items():
            html.append(f"<tr><td>{k}</td><td>{v}</td></tr>")

        html.append("</table><h2>Column Statistics</h2>")
        html.append(
            "<table><tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th><th>Mean</th><th>Min</th><th>P25</th><th>Median</th><th>P75</th><th>Max</th></tr>"
        )

        for col, stats in self.column_stats.items():
            html.append("<tr>")
            html.append(f"<td>{col}</td>")
            html.append(f"<td>{stats.get('type', '')}</td>")
            html.append(f"<td>{stats.get('missing', '')}</td>")
            html.append(f"<td>{stats.get('unique', '')}</td>")
            html.append(f"<td>{stats.get('mean', '')}</td>")
            html.append(f"<td>{stats.get('min', '')}</td>")
            html.append(f"<td>{stats.get('p25', '')}</td>")
            html.append(f"<td>{stats.get('median', '')}</td>")
            html.append(f"<td>{stats.get('p75', '')}</td>")
            html.append(f"<td>{stats.get('max', '')}</td>")
            html.append("</tr>")

        html.append("</table></body></html>")
        return "\n".join(html)
