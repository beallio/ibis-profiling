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

            if n > 0 and "n_distinct" in stats:
                stats["distinct_perc"] = stats["n_distinct"] / n

    def add_metric(self, col_name: str, metric_name: str, value: any):
        """Manually adds a metric result to the report."""
        val = self._to_json_serializable(value)
        if col_name == "_dataset":
            self.dataset_stats[metric_name] = val
        else:
            if col_name not in self.column_stats:
                self.column_stats[col_name] = {}
            self.column_stats[col_name][metric_name] = val

    def to_dict(self):
        return {"dataset": self.dataset_stats, "columns": self.column_stats}

    def get_description(self) -> dict:
        """Alias for to_dict() to match ydata-profiling API."""
        return self.to_dict()

    def to_json(self) -> str:
        """Returns the report as a JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=2)

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
        """Generates the HTML report using one of the 5 available templates."""
        import json

        if template == "ydata":
            return self._template_ydata(json)
        elif template == "modern":
            return self._template_modern(json)
        elif template == "executive":
            return self._template_executive(json)
        elif template == "dense":
            return self._template_dense(json)
        else:
            return self._template_minimal()

    def _template_ydata(self, json) -> str:
        """Near-exact mimicry of the ydata-profiling HTML report."""
        html = [
            "<!doctype html><html lang=en><head>",
            "<meta charset=utf-8><meta content='width=device-width,initial-scale=1,shrink-to-fit=no' name=viewport>",
            "<title>Ibis Profiling Report</title>",
            "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>",
            "<script src='https://cdn.plot.ly/plotly-2.24.1.min.js'></script>",
            "<style>",
            "body { font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif; font-size: 14px; color: #333; }",
            ".navbar { background-color: #f8f9fa !important; border-bottom: 1px solid #ddd; padding: 10px 0; }",
            ".navbar-brand { font-weight: 700; color: #333 !important; }",
            ".section-header { margin-top: 40px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }",
            ".section-name { font-size: 28px; font-weight: 700; }",
            ".row.item { margin-bottom: 30px; }",
            ".item-header { font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #444; }",
            ".table th { font-weight: 600; color: #666; background-color: transparent !important; }",
            ".variable { padding: 20px 0; border-bottom: 1px solid #eee; }",
            ".var-name { font-family: monospace; font-weight: 700; font-size: 1.2rem; color: #007bff; text-decoration: none; }",
            ".badge { text-transform: uppercase; padding: 4px 8px; font-weight: 500; font-size: 11px; }",
            ".text-bg-danger { background-color: #dc3545; }",
            ".text-bg-info { background-color: #0dcaf0; }",
            ".bar { background-color: #007bff; height: 18px; color: white; padding: 0 5px; font-size: 11px; line-height: 18px; border-radius: 2px; }",
            "</style>",
            "</head><body>",
            "<nav class='navbar navbar-expand-lg sticky-top'><div class='container-fluid'>",
            "<a class='navbar-brand' href='#'>Ibis Profiling Report</a>",
            "<div class='collapse navbar-collapse'><ul class='navbar-nav ms-auto'>",
            "<li class='nav-item'><a class='nav-link' href='#overview'>Overview</a></li>",
            "<li class='nav-item'><a class='nav-link' href='#variables'>Variables</a></li>",
            "<li class='nav-item'><a class='nav-link' href='#sample'>Sample</a></li>",
            "</ul></div></div></nav>",
            "<div class='container mt-4'>",
            # Overview Section
            "<div class='section-header' id='overview'><h1 class='section-name'>Overview</h1></div>",
            "<div class='row item'><ul class='nav nav-tabs tab-nav mb-3' role='tablist'>",
            "<li class='nav-item'><button class='nav-link active' data-bs-toggle='tab' data-bs-target='#tab-overview' type='button'>Overview</button></li>",
            "<li class='nav-item'><button class='nav-link' data-bs-toggle='tab' data-bs-target='#tab-alerts' type='button'>Alerts</button></li>",
            "</ul>",
            "<div class='tab-content'>",
            "<div class='tab-pane fade show active' id='tab-overview'><div class='row sub-item'>",
            "<div class='col-sm-6'><p class='h4 item-header'>Dataset statistics</p><table class='table table-striped'><tbody>",
        ]

        # Dataset Stats
        ds_stats = [
            ("Number of variables", self.dataset_stats.get("n_var")),
            ("Number of observations", self.dataset_stats.get("row_count")),
            ("Missing cells", self.dataset_stats.get("missing_cells")),
            ("Missing cells (%)", f"{self.dataset_stats.get('missing_cells_perc', 0):.1%}"),
            ("Duplicate rows", self.dataset_stats.get("duplicate_rows", 0)),
        ]
        for label, val in ds_stats:
            v = f"{val:,}" if isinstance(val, int) else val
            html.append(f"<tr><th>{label}</th><td>{v}</td></tr>")

        html.append("</tbody></table></div>")

        # Variable Types
        html.append(
            "<div class='col-sm-6'><p class='h4 item-header'>Variable types</p><table class='table table-striped'><tbody>"
        )
        types = {}
        for s in self.column_stats.values():
            t = s.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
        for t, count in types.items():
            html.append(f"<tr><th>{t.capitalize()}</th><td>{count}</td></tr>")
        html.append("</tbody></table></div></div></div>")

        # Alerts (Dynamic)
        html.append(
            "<div class='tab-pane fade' id='tab-alerts'><table class='table table-striped'>"
        )
        alerts_found = 0
        for col, stats in self.column_stats.items():
            if stats.get("n_distinct") == self.dataset_stats.get("row_count"):
                html.append(
                    f"<tr><td><code>{col}</code> has unique values</td><td><span class='badge text-bg-danger'>Unique</span></td></tr>"
                )
                alerts_found += 1
            if stats.get("zeros", 0) > 0:
                z_perc = stats.get("zeros", 0) / self.dataset_stats.get("row_count", 1)
                html.append(
                    f"<tr><td><code>{col}</code> has {stats.get('zeros'):,} ({z_perc:.1%}) zeros</td><td><span class='badge text-bg-info'>Zeros</span></td></tr>"
                )
                alerts_found += 1
        if alerts_found == 0:
            html.append("<tr><td>No alerts detected.</td></tr>")
        html.append("</table></div></div></div>")

        # Variables Section
        html.append(
            "<div class='section-header' id='variables'><h1 class='section-name'>Variables</h1></div>"
        )
        for i, (col, stats) in enumerate(self.column_stats.items()):
            html.append(f"<div class='variable row item' id='var-{col}'><div class='row sub-item'>")
            # Header
            html.append(
                f"<div class='col-sm-12'><p class='item-header h4'><a class='var-name' href='#var-{col}'>{col}</a><br>"
            )
            html.append(
                f"<span class='fs-6 text-body-secondary text-uppercase'>{stats.get('type')}</span></p></div>"
            )

            # Left Column: Basic Stats
            html.append("<div class='col-sm-6'><table class='table table-striped'><tbody>")
            v_metrics = [
                ("Distinct", stats.get("n_distinct", 0)),
                ("Distinct (%)", f"{stats.get('distinct_perc', 0):.1%}"),
                ("Missing", stats.get("missing", 0)),
                (
                    "Missing (%)",
                    f"{(stats.get('missing', 0) / self.dataset_stats.get('row_count', 1)):.1%}",
                ),
            ]
            if stats.get("mean") is not None:
                v_metrics += [
                    ("Mean", f"{stats.get('mean', 0):.4f}"),
                    ("Minimum", stats.get("min")),
                    ("Maximum", stats.get("max")),
                    ("Zeros", f"{stats.get('zeros', 0):,}"),
                ]
            for label, val in v_metrics:
                v_str = f"{val:,}" if isinstance(val, int) else str(val)
                html.append(f"<tr><th>{label}</th><td>{v_str}</td></tr>")
            html.append("</tbody></table></div>")

            # Right Column: Mini-Histogram/Plot
            html.append("<div class='col-sm-6'>")
            if "top_values" in stats:
                chart_id = f"chart-{i}"
                top_vals = stats["top_values"]
                counts = list(top_vals.get(f"{col}_count", []))
                labels = [str(x) for x in top_vals.get(col, [])]
                html.append(f"<div id='{chart_id}' style='height: 250px;'></div>")
                html.append(
                    f"<script>Plotly.newPlot('{chart_id}', [{{x: {json.dumps(labels)}, y: {json.dumps(counts)}, type: 'bar', marker: {{color: '#007bff'}}}}], "
                )
                html.append(
                    "{margin: {t: 10, b: 40, l: 50, r: 10}, height: 250, font: {size: 11}, xaxis: {tickangle: -45}});</script>"
                )
            html.append("</div>")

            html.append("</div></div>")

        # Sample Section
        html.append(
            "<div class='section-header' id='sample'><h1 class='section-name'>Sample</h1></div>"
        )
        sample = self.dataset_stats.get("head")
        if sample:
            html.append(
                "<div class='table-responsive'><table class='table table-sm table-striped border'><thead><tr>"
            )
            cols = list(sample.keys())
            for c in cols:
                html.append(f"<th>{c}</th>")
            html.append("</tr></thead><tbody>")
            n_rows = len(sample[cols[0]])
            for r in range(n_rows):
                html.append("<tr>")
                for c in cols:
                    html.append(f"<td>{sample[c][r]}</td>")
                html.append("</tr>")
            html.append("</tbody></table></div>")

        html.append(
            "</div><script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'></script></body></html>"
        )
        return "\n".join(html)

    def _template_modern(self, json) -> str:
        """Dark mode, glowing futuristic dashboard."""
        html = [
            "<!DOCTYPE html><html><head><title>Ibis Modern</title>",
            "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>",
            "<style>body { background: #0f172a; color: #e2e8f0; font-family: sans-serif; }",
            ".glass-card { background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px); }",
            ".accent-text { color: #38bdf8; font-weight: bold; }",
            "h1 { font-weight: 800; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }",
            ".badge { background: #334155; color: #38bdf8; border: 1px solid #38bdf8; }",
            "</style></head><body><div class='container py-5'>",
            "<h1>Modern Analytics</h1><hr class='opacity-10 mb-5'>",
            "<div class='row'>",
        ]
        # Summary
        for k, v in self.dataset_stats.items():
            if not isinstance(v, (int, float)):
                continue
            html.append(
                f"<div class='col-md-3'><div class='glass-card text-center'><div class='text-secondary small text-uppercase'>{k}</div><div class='fs-2 accent-text'>{v:,}</div></div></div>"
            )

        html.append("</div><h2 class='mt-5 mb-4'>Variable Insights</h2>")
        for col, stats in self.column_stats.items():
            html.append(
                f"<div class='glass-card'><div class='d-flex justify-content-between mb-3'><h3>{col}</h3><span class='badge'>{stats.get('type')}</span></div>"
            )
            html.append("<div class='row'>")
            for m in ["mean", "min", "max", "n_distinct"]:
                if stats.get(m) is not None:
                    v = stats[m]
                    val = (
                        f"{v:.4f}"
                        if isinstance(v, float)
                        else f"{v:,}"
                        if isinstance(v, int)
                        else v
                    )
                    html.append(
                        f"<div class='col-md-3 text-center border-end border-secondary'><div class='small text-secondary'>{m.upper()}</div><div>{val}</div></div>"
                    )
            html.append("</div></div>")

        html.append("</div></body></html>")
        return "\n".join(html)

    def _template_executive(self, json) -> str:
        """High-level summary focus for decision makers."""
        html = [
            "<!DOCTYPE html><html><head><title>Executive Summary</title>",
            "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>",
            "<style>body { font-family: 'Georgia', serif; padding: 60px; background: #fff; }",
            ".kpi-box { border-top: 4px solid #333; padding-top: 15px; margin-bottom: 40px; }",
            "table { border-top: 2px solid #333; }",
            "</style></head><body>",
            "<h1>Data Integrity Executive Report</h1><p class='text-muted'>Generated on "
            + datetime.now().strftime("%Y-%m-%d")
            + "</p>",
            "<div class='row mt-5'>",
        ]
        # Big KPIs
        n = self.dataset_stats.get("row_count", 0)
        html.append(
            f"<div class='col-md-4 kpi-box'><h3>Total Records</h3><div class='display-4'>{n:,}</div></div>"
        )
        html.append(
            f"<div class='col-md-4 kpi-box'><h3>Total Columns</h3><div class='display-4'>{len(self.column_stats)}</div></div>"
        )
        missing = self.dataset_stats.get("missing_cells_perc", 0)
        html.append(
            f"<div class='col-md-4 kpi-box'><h3>Missing Data</h3><div class='display-4'>{missing:.1%}</div></div>"
        )

        html.append(
            "</div><h2 class='mt-5'>Variable Summary</h2><table class='table table-hover mt-3'><thead><tr><th>Name</th><th>Type</th><th>Distinct</th><th>Missing</th><th>Mean</th></tr></thead><tbody>"
        )
        for col, stats in self.column_stats.items():
            html.append(
                f"<tr><td>{col}</td><td>{stats.get('type')}</td><td>{stats.get('n_distinct')}</td><td>{stats.get('missing')}</td><td>{stats.get('mean', 'N/A')}</td></tr>"
            )
        html.append("</tbody></table></body></html>")
        return "\n".join(html)

    def _template_dense(self, json) -> str:
        """Compact spreadsheet-like grid for large schemas."""
        html = [
            "<!DOCTYPE html><html><head><title>Dense View</title>",
            "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>",
            "<style>body { font-size: 11px; padding: 10px; font-family: monospace; }",
            "table { width: 100%; border-collapse: collapse; }",
            "th { background: #eee; position: sticky; top: 0; }",
            "td, th { border: 1px solid #ccc; padding: 2px 5px; }",
            "tr:hover { background: #ffffcc; }</style></head><body>",
            "<h3>Dense Grid Profile - " + str(self.dataset_stats.get("row_count")) + " rows</h3>",
            "<table><thead><tr><th>Variable</th><th>Type</th><th>Distinct</th><th>Unique</th><th>Missing</th><th>Mean</th><th>Min</th><th>Median</th><th>Max</th><th>Std</th></tr></thead><tbody>",
        ]
        for col, stats in self.column_stats.items():
            html.append(f"<tr><td>{col}</td><td>{stats.get('type')}</td>")
            for m in [
                "n_distinct",
                "n_unique",
                "missing",
                "mean",
                "min",
                "median",
                "max",
                "std",
            ]:
                val = stats.get(m, "")
                if isinstance(val, float):
                    val = f"{val:.2f}"
                html.append(f"<td>{val}</td>")
            html.append("</tr>")
        html.append("</tbody></table></body></html>")
        return "\n".join(html)

    def _template_minimal(self) -> str:
        """Simple, clean Bootstrap dashboard."""
        html = [
            "<!DOCTYPE html><html><head><title>Minimal Profile</title>",
            "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>",
            "</head><body class='bg-light'><div class='container py-5'>",
            "<div class='card p-4 mb-4'><h1>Simple Data Profile</h1>",
        ]
        html.append(
            f"<p>Rows: {self.dataset_stats.get('row_count'):,} | Columns: {len(self.column_stats)}</p></div>"
        )
        for col, stats in self.column_stats.items():
            html.append(
                f"<div class='card p-3 mb-2'><strong>{col}</strong> ({stats.get('type')}) - Mean: {stats.get('mean', 'N/A')}</div>"
            )
        html.append("</div></body></html>")
        return "\n".join(html)
