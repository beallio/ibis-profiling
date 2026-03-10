import pandas as pd


class ProfileReport:
    def __init__(self, raw_results: pd.DataFrame, schema: dict):
        self.raw_results = raw_results
        self.schema = schema
        self.dataset_stats = {}
        self.column_stats = {}
        self._build()

    def _to_json_serializable(self, val):
        """Converts NumPy/Pandas types to standard Python types for JSON serialization."""
        if hasattr(val, "item"):
            return val.item()
        if hasattr(val, "to_pydatetime"):
            return val.to_pydatetime().isoformat()
        if hasattr(val, "isoformat"):
            return val.isoformat()
        return val

    def _build(self):
        if self.raw_results.empty:
            return

        row = self.raw_results.iloc[0]  # Single row containing all aggregates

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
            "<table><tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th><th>Min</th><th>Max</th><th>Mean</th></tr>"
        )

        for col, stats in self.column_stats.items():
            html.append("<tr>")
            html.append(f"<td>{col}</td>")
            html.append(f"<td>{stats.get('type', '')}</td>")
            html.append(f"<td>{stats.get('missing', '')}</td>")
            html.append(f"<td>{stats.get('unique', '')}</td>")
            html.append(f"<td>{stats.get('min', '')}</td>")
            html.append(f"<td>{stats.get('max', '')}</td>")
            html.append(f"<td>{stats.get('mean', '')}</td>")
            html.append("</tr>")

        html.append("</table></body></html>")
        return "\n".join(html)
