import polars as pl
from datetime import datetime, date
import json
import os
import math
import base64
from typing import Any, cast
from .model.summary import SummaryEngine
from .model.alerts import AlertEngine


class ReportEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        import ibis.expr.types as ir
        from decimal import Decimal

        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, ir.Scalar):
            try:
                val = o.to_pyarrow().as_py()
            except Exception:
                val = str(o)
        else:
            val = o

        if hasattr(val, "item") and callable(getattr(val, "item", None)):
            val = cast(Any, val).item()

        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
            return val

        if isinstance(val, Decimal):
            return float(val)

        # Final check if val is same as o and it's not a primitive, we might still fail
        if val is o and not isinstance(val, (str, int, float, bool, list, dict, type(None))):
            return super().default(o)

        return val


class ProfileReport:
    """Canonical Report Model that assembles data from specialized engines."""

    def __init__(
        self, raw_results: pl.DataFrame, schema: dict, title: str = "Ibis Profiling Report"
    ):
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
        self.analysis: dict[str, Any] = {
            "title": title,
            "date_start": datetime.now().isoformat(),
        }

        self._build()
        self.analysis["date_end"] = datetime.now().isoformat()

    def _to_json_serializable(self, val):
        """Converts Polars/Temporal/Ibis types to standard Python types for JSON serialization."""
        import ibis.expr.types as ir
        from decimal import Decimal

        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if isinstance(val, Decimal):
            return float(val)
        if isinstance(val, ir.Scalar):
            try:
                # Use to_pyarrow() for robust conversion, then to_py()
                val = val.to_pyarrow().as_py()
            except Exception:
                # If conversion fails, don't just return str(val) if it might be used numerically
                # but for general report data, string is the safest fallback if we can't get the value
                # Log a warning or similar if we had a logger
                return str(val)

        if hasattr(val, "item") and callable(getattr(val, "item", None)):
            val = val.item()

        # Handle NaN/Inf which break strict JSON
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None

        if isinstance(val, (str, int, float, bool, list, dict, type(None))):
            return val

        # Final fallback: string representation with a marker
        return f"__unsupported_type__:{type(val).__name__}:{str(val)}"

    def _build(self):
        # 1. Variables Summary
        # Temporarily store _dataset if it exists in schema
        schema_copy = dict(self.schema)
        dataset_meta = schema_copy.pop("_dataset", {})
        self.variables = SummaryEngine.process_variables(self.raw_results, schema_copy)

        # 2. Table Summary
        n = 0
        if not self.raw_results.is_empty():
            row = self.raw_results.row(0, named=True)
            n = row.get("_dataset__row_count", 0)

            self.table = {
                "n": n,
                "n_var": len(self.variables),
                "memory_size": self._to_json_serializable(dataset_meta.get("memory_size", 0)),
                "record_size": self._to_json_serializable(dataset_meta.get("record_size", 0)),
                "n_cells_missing": 0,
                "n_vars_with_missing": 0,
                "n_vars_all_missing": 0,
                "n_vars_constant": 0,
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
            m_count = stats.get("n_missing")
            if m_count is None:
                m_count = 0
            stats["n_missing"] = self._to_json_serializable(m_count)
            stats["p_missing"] = self._to_json_serializable(m_count / n if n > 0 else 0)
            stats["p_distinct"] = self._to_json_serializable(
                stats.get("n_distinct", 0) / n if n > 0 else 0
            )

            stats["count"] = n - m_count
            stats["is_unique"] = stats.get("n_distinct", 0) == n

            # Constant detection
            if stats.get("n_distinct", 0) == 1:
                current_c = self.table.get("n_vars_constant", 0)
                if isinstance(current_c, int):
                    self.table["n_vars_constant"] = current_c + 1

            n_cells_missing += m_count
            if m_count > 0:
                current_wm = self.table.get("n_vars_with_missing", 0)
                if isinstance(current_wm, int):
                    self.table["n_vars_with_missing"] = current_wm + 1
            if m_count == n and n > 0:
                current_am = self.table.get("n_vars_all_missing", 0)
                if isinstance(current_am, int):
                    self.table["n_vars_all_missing"] = current_am + 1

            # Derived Numeric Stats
            if stats.get("type") == "Numeric":
                # Range
                if stats.get("max") is not None and stats.get("min") is not None:
                    stats["range"] = stats["max"] - stats["min"]

                # IQR
                if stats.get("75%") is not None and stats.get("25%") is not None:
                    stats["iqr"] = stats["75%"] - stats["25%"]

                # CV
                if (
                    stats.get("std") is not None
                    and stats.get("mean") is not None
                    and stats["mean"] != 0
                ):
                    stats["cv"] = stats["std"] / stats["mean"]

                # Zeros Percentage
                if stats.get("n_zeros") is not None:
                    stats["p_zeros"] = stats["n_zeros"] / n if n > 0 else 0

                # Infinite Percentage
                if stats.get("n_infinite") is not None:
                    stats["p_infinite"] = stats["n_infinite"] / n if n > 0 else 0

                # Negative Percentage
                if stats.get("n_negative") is not None:
                    stats["p_negative"] = stats["n_negative"] / n if n > 0 else 0
            elif stats.get("type") == "Categorical":
                # For categoricals, we don't want continuous numeric metrics
                # even if they were calculated in pass 1 before reclassification
                for k in [
                    "mean",
                    "std",
                    "variance",
                    "skewness",
                    "kurtosis",
                    "mad",
                    "sum",
                    "50%",
                    "5%",
                    "25%",
                    "75%",
                    "95%",
                ]:
                    stats.pop(k, None)

            # Unique Percentage
            if stats.get("n_unique") is not None:
                stats["p_unique"] = stats["n_unique"] / n if n > 0 else 0

            # Ensure other stats are serializable
            for k, v in list(stats.items()):
                stats[k] = self._to_json_serializable(v)

        if self.table:
            self.table["n_cells_missing"] = n_cells_missing
            n_var = self.table.get("n_var", 0)
            if isinstance(n_var, int) and n > 0 and n_var > 0:
                self.table["p_cells_missing"] = n_cells_missing / (n * n_var)
            else:
                self.table["p_cells_missing"] = 0

        # 4. Generate Alerts
        self.alerts = AlertEngine.get_alerts(self.table, self.variables)

    def add_metric(self, col_name: str, metric_name: str, value: Any):
        """Adds extra data like samples or histograms to the model."""
        if metric_name in ["head", "tail"]:
            self.samples[metric_name] = value
        elif col_name in self.variables:
            # Handle complex mapping like histograms
            if metric_name == "top_values":
                # Ibis value_counts() returns [col_name, count_col]
                # We use positional indexing for robustness
                keys = list(value.keys())
                if len(keys) >= 2:
                    label_key = keys[0]
                    count_key = keys[1]

                    counts = list(value.get(count_key, []))
                    labels = []
                    for x in value.get(label_key, []):
                        if isinstance(x, (datetime, date)):
                            labels.append(x.isoformat())
                        else:
                            labels.append(str(x))
                    self.variables[col_name]["histogram"] = {"bins": labels, "counts": counts}

            elif metric_name == "numeric_histogram":
                # Data is binned: {bin_idx: count, ...} + metadata
                # We expect value to be a dict: {'counts': {idx: count}, 'min': val, 'max': val, 'nbins': val}
                counts_dict = value.get("counts", {})
                v_min = value.get("min", 0)
                v_max = value.get("max", 0)
                nbins = value.get("nbins", 20)

                if v_max == v_min:
                    # Constant data
                    self.variables[col_name]["histogram"] = {
                        "bins": [str(v_min)],
                        "counts": [sum(counts_dict.values())],
                    }
                    return

                bin_width = (v_max - v_min) / nbins

                # Reconstruct full range even for empty bins
                all_counts = []
                all_labels = []
                for i in range(nbins):
                    b_start = v_min + (i * bin_width)
                    b_end = v_min + ((i + 1) * bin_width)
                    all_labels.append(f"[{b_start:.2f}, {b_end:.2f}]")
                    all_counts.append(counts_dict.get(i, 0))

                self.variables[col_name]["histogram"] = {"bins": all_labels, "counts": all_counts}

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
        from .. import __version__

        pkg_version = __version__

        d = {
            "analysis": self.analysis,
            "table": self.table,
            "variables": self.variables,
            "correlations": self._format_matrices(self.correlations),
            "interactions": self.interactions,
            "missing": self._format_matrices(self.missing),
            "alerts": self.alerts,
            "sample": self.samples,
            "package": {"name": "ibis-profiling", "version": pkg_version},
        }
        return self._clean_dict(d)

    def _format_matrices(self, obj: Any) -> Any:
        """
        Recursively transforms {columns, matrix} objects to {matrix: list-of-dicts, metadata}.
        Preserves flags like 'sampled'.
        """
        if isinstance(obj, dict):
            # Check if this specific dict is a matrix container
            if "columns" in obj and "matrix" in obj and isinstance(obj["matrix"], list):
                cols = obj["columns"]
                matrix = obj["matrix"]
                # Only transform if it's the raw [ [v1, v2], [v3, v4] ] format
                if matrix and isinstance(matrix[0], list):
                    formatted_matrix = [dict(zip(cols, row)) for row in matrix]
                    # Create result with matrix and any other metadata (like 'sampled')
                    res = {"matrix": formatted_matrix}
                    for k, v in obj.items():
                        if k not in ["columns", "matrix"]:
                            res[k] = v
                    return res

            # Continue recursing for all keys
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

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, cls=ReportEncoder)

    def to_file(self, output_file: str, theme: str = "default", minify: bool = True):
        content = (
            self.to_json()
            if output_file.endswith(".json")
            else self.to_html(theme=theme, minify=minify)
        )
        with open(output_file, "w") as f:
            f.write(content)

    def to_html(self, theme: str = "default", minify: bool = True) -> str:
        ALLOWED_THEMES = {"default", "ydata-like"}

        # 1. Allowlist validation
        if theme not in ALLOWED_THEMES:
            self.analysis.setdefault("warnings", [])
            self.analysis["warnings"].append(
                f"Invalid theme '{theme}' requested. Falling back to 'default'."
            )
            theme = "default"

        template_name = f"{theme}.html"
        templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
        template_path = os.path.join(templates_dir, template_name)

        # 2. Path traversal protection (realpath check)
        # We use os.path.commonpath for more robust prefix checking
        real_templates_dir = os.path.realpath(templates_dir)
        real_template_path = os.path.realpath(template_path)

        if os.path.commonpath([real_templates_dir, real_template_path]) != real_templates_dir:
            self.analysis.setdefault("warnings", [])
            self.analysis["warnings"].append(
                f"Security: Theme path '{theme}' attempted to escape templates directory. Falling back to 'default'."
            )
            template_path = os.path.join(templates_dir, "default.html")

        if not os.path.exists(template_path):
            # Fallback to default if theme file not found
            template_path = os.path.join(templates_dir, "default.html")

        with open(template_path, "r") as f:
            html = f.read()

        # Minify JSON for embedding (separators removes extra spaces)
        report_json = json.dumps(self.to_dict(), separators=(",", ":"), cls=ReportEncoder)

        # Base64 encode the JSON for secure embedding in a data-attribute
        # This completely avoids XSS from the JSON data
        encoded_json = base64.b64encode(report_json.encode("utf-8")).decode("utf-8")

        if minify:
            import re

            # 1. Remove HTML comments
            html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
            # 2. Remove CSS/JS multi-line comments
            html = re.sub(r"/\*.*?\*/", "", html, flags=re.DOTALL)
            # 3. Safer minification: strip leading/trailing whitespace from each line
            html = "\n".join([line.strip() for line in html.splitlines() if line.strip()])

        # Replace data-report attribute with our encoded JSON
        # We assume the template has <div id="report-data" data-report="{{REPORT_DATA}}"></div>
        # or similar. If it's a raw script tag like before, we update the JS to decode it.
        return html.replace("{{REPORT_DATA}}", encoded_json)

    @staticmethod
    def from_excel(path: str, **kwargs) -> "ProfileReport":
        """Convenience method to profile an Excel file."""
        import polars as pl
        import ibis
        from .. import profile

        import inspect

        # Separate read_excel kwargs from profile kwargs using profile signature
        sig = inspect.signature(profile)
        profile_keys = set(sig.parameters.keys())

        profile_kwargs = {k: v for k, v in kwargs.items() if k in profile_keys}
        read_kwargs = {k: v for k, v in kwargs.items() if k not in profile_keys}

        # Use calamine for high performance (requires fastexcel)
        df = pl.read_excel(path, engine="calamine", **read_kwargs)
        table = ibis.memtable(df)
        return profile(table, **profile_kwargs)

    def get_description(self) -> dict:
        return self.to_dict()
