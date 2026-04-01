import polars as pl
from datetime import datetime, date
import json
import os
import math
import base64
from typing import Any, cast
from decimal import Decimal
import ibis.expr.types as ir
from .model.summary import SummaryEngine
from .model.alerts import AlertEngine
from ..constants import NUMERIC_ONLY_METRICS


def serialize_report_value(val: Any) -> Any:
    """
    Unified utility to convert various types (Ibis, Polars, Temporal)
    to JSON-serializable Python primitives.
    """
    if val is None:
        return None

    # 1. Handle Ibis Scalars first (they might resolve to other complex types)
    if isinstance(val, ir.Scalar):
        try:
            val = val.to_pyarrow().as_py()
            # Recursive call to handle the result (e.g. if it's a datetime or Decimal)
            return serialize_report_value(val)
        except Exception:
            return str(val)

    # 2. Handle Temporal types
    if isinstance(val, (datetime, date)):
        return val.isoformat()

    # 3. Handle Decimal
    if isinstance(val, Decimal):
        val = float(val)
        # Proceed to float check for NaN/Inf

    # 4. Handle Objects with .item() (e.g. numpy/pandas scalars)
    if hasattr(val, "item") and callable(getattr(val, "item", None)):
        val = cast(Any, val).item()

    # 5. Handle Floats (including those from Decimal/item)
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return val

    # 6. Return primitives as-is
    if isinstance(val, (str, int, bool, list, dict)):
        return val

    return val


class ReportEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        res = serialize_report_value(o)
        # If serialize_report_value returned the same object and it's not a primitive,
        # fallback to the default encoder behavior.
        if res is o and not isinstance(res, (str, int, float, bool, list, dict, type(None))):
            return super().default(o)
        return res


class ProfileReport:
    """Canonical Report Model that assembles data from specialized engines."""

    _asset_cache: dict[str, str] = {}

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

    def reclassify(self, col_name: str, new_type: str):
        """Changes the type of a variable and cleans up incompatible metadata."""
        if col_name not in self.variables:
            return

        stats = self.variables[col_name]
        old_type = stats.get("type")
        if old_type == new_type:
            return

        stats["type"] = new_type

        # Update table type counts
        if self.table and isinstance(self.table.get("types"), dict):
            types = cast(dict, self.table["types"])
            old_type_str = cast(str, old_type)
            if old_type_str in types:
                types[old_type_str] -= 1
            types[new_type] = types.get(new_type, 0) + 1

        # Cleanup metadata
        if new_type == "Categorical":
            for k in NUMERIC_ONLY_METRICS:
                stats.pop(k, None)

    def _to_json_serializable(self, val):
        """Converts Polars/Temporal/Ibis types to standard Python types for JSON serialization."""
        res = serialize_report_value(val)
        if isinstance(res, (str, int, float, bool, list, dict, type(None))):
            return res

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

        # 3. Post-process variables (basic metadata needed for next passes)
        for col, stats in self.variables.items():
            stats["n"] = n
            m_count = stats.get("n_missing", 0)
            # Store raw numeric for calculation, serialize later in finalize()
            stats["n_missing"] = m_count
            stats["count"] = n - (m_count if isinstance(m_count, (int, float)) else 0)

    def finalize(self):
        """Finalizes the report by calculating derived metrics and generating alerts."""
        if not self.table or not isinstance(self.table.get("n"), (int, float)):
            return

        n = cast(int, self.table["n"])

        # Reset table counters for idempotency
        self.table["n_cells_missing"] = 0
        self.table["n_vars_with_missing"] = 0
        self.table["n_vars_all_missing"] = 0
        self.table["n_vars_constant"] = 0

        n_cells_missing = 0

        # Post-process variables (normalization & derived metrics)
        for col, stats in self.variables.items():
            m_count = stats.get("n_missing", 0)
            if not isinstance(m_count, (int, float)):
                m_count = 0

            stats["p_missing"] = m_count / n if n > 0 else 0

            n_distinct = stats.get("n_distinct")
            if isinstance(n_distinct, (int, float)):
                stats["p_distinct"] = n_distinct / n if n > 0 else 0

                # Constant detection
                if n_distinct == 1:
                    self.table["n_vars_constant"] = cast(int, self.table["n_vars_constant"]) + 1
            else:
                stats["p_distinct"] = n_distinct  # Likely "Skipped"

            stats["count"] = n - m_count

            if isinstance(n_distinct, (int, float)):
                stats["is_unique"] = n > 0 and n_distinct == n
            else:
                stats["is_unique"] = False

            # Explicitly accumulate into local variable
            n_cells_missing += m_count

            if m_count > 0:
                self.table["n_vars_with_missing"] = cast(int, self.table["n_vars_with_missing"]) + 1

            if m_count == n and n > 0:
                self.table["n_vars_all_missing"] = cast(int, self.table["n_vars_all_missing"]) + 1

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
                for k in NUMERIC_ONLY_METRICS:
                    stats.pop(k, None)

            # Unique Percentage (Updated after add_metric calls)
            n_unique = stats.get("n_unique")
            if n_unique is not None:
                if isinstance(n_unique, (int, float)):
                    stats["p_unique"] = n_unique / n if n > 0 else 0
                else:
                    stats["p_unique"] = n_unique  # Likely "Skipped"

            # Ensure other stats are serializable
            for k, v in list(stats.items()):
                stats[k] = self._to_json_serializable(v)

        self.table["n_cells_missing"] = n_cells_missing
        n_var = self.table.get("n_var", 0)
        if isinstance(n_var, int) and n > 0 and n_var > 0:
            self.table["p_cells_missing"] = n_cells_missing / (n * n_var)
        else:
            self.table["p_cells_missing"] = 0

        # Generate Alerts
        self.alerts = AlertEngine.get_alerts(self.table, self.variables)

    def add_metric(self, col_name: str, metric_name: str, value: Any):
        """Adds extra data like samples or histograms to the model."""
        if metric_name in ["head", "tail"]:
            self.samples[metric_name] = value
        elif col_name in self.variables:
            # Handle skipped metrics
            if value == "Skipped":
                self.variables[col_name][metric_name] = "Skipped"
                return

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
        self.finalize()
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
                    # We keep 'columns' because some components (like MissingMatrix) need the order
                    res = {"matrix": formatted_matrix, "columns": cols}
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
        """Recursively replaces non-serializable types with JSON primitives."""
        if isinstance(obj, dict):
            return {str(k): self._clean_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_dict(v) for v in obj]
        else:
            return serialize_report_value(obj)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, cls=ReportEncoder)

    def to_file(
        self, output_file: str, theme: str = "default", minify: bool = True, offline: bool = True
    ):
        content = (
            self.to_json()
            if output_file.endswith(".json")
            else self.to_html(theme=theme, minify=minify, offline=offline)
        )
        with open(output_file, "w") as f:
            f.write(content)

    def to_html(self, theme: str = "default", minify: bool = True, offline: bool = True) -> str:
        import secrets

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
        vendor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vendor", "js"))
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

        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()

        # 3. Asset Injection
        assets = {
            "TAILWIND": {
                "file": "tailwind.min.js",
                "url": "https://cdn.tailwindcss.com/3.4.1",
                "sri": "sha384-igm5BeiBt36UU4gqwWS7imYmelpTsZlQ45FZf+XBn9MuJbn4nQr7yx1yFydocC/K",
            },
            "REACT": {
                "file": "react.production.min.js",
                "url": "https://unpkg.com/react@18.2.0/umd/react.production.min.js",
                "sri": "sha384-tMH8h3BGESGckSAVGZ82T9n90ztNXxvdwvdM6UoR56cYcf+0iGXBliJ29D+wZ/x8",
            },
            "REACT_DOM": {
                "file": "react-dom.production.min.js",
                "url": "https://unpkg.com/react-dom@18.2.0/umd/react-dom.production.min.js",
                "sri": "sha384-bm7MnzvK++ykSwVJ2tynSE5TRdN+xL418osEVF2DE/L/gfWHj91J2Sphe582B1Bh",
            },
            "LUCIDE": {
                "file": "lucide-react.min.js",
                "url": "https://unpkg.com/lucide-react@0.292.0/dist/umd/lucide-react.min.js",
                "sri": "sha384-F0qUHZkh0kdyj05DoGn8B9QgQ7vnQLjO74ZwZNMSrJINJv7um6jfha6Imsr0HK0T",
            },
        }

        # 4. Content Security Policy (CSP) & Nonce
        nonce = secrets.token_hex(16)
        csp_directives = [
            "default-src 'self'",
            f"script-src 'nonce-{nonce}'",
            "style-src 'unsafe-inline'",
            "img-src 'self' data: blob: https://raw.githubusercontent.com",
            "font-src 'self' data:",
        ]

        if offline:
            # Inline all assets (using a simple module-level cache to avoid redundant I/O)
            for name, meta in assets.items():
                placeholder = f"{{{{{name}_SCRIPT}}}}"
                if meta["file"] not in ProfileReport._asset_cache:
                    asset_path = os.path.join(vendor_dir, meta["file"])
                    with open(asset_path, "r", encoding="utf-8") as f:
                        ProfileReport._asset_cache[meta["file"]] = f.read()

                content = ProfileReport._asset_cache[meta["file"]]
                # Security: Escape </script> to avoid script breakouts
                content = content.replace("</script", "<\\/script")
                html = html.replace(
                    placeholder, f'<script nonce="{{{{NONCE}}}}">{content}</script>'
                )

            csp_directives.append("connect-src 'none'")
        else:
            # Use CDN links
            for name, meta in assets.items():
                placeholder = f"{{{{{name}_SCRIPT}}}}"
                html = html.replace(
                    placeholder,
                    f'<script nonce="{{{{NONCE}}}}" src="{meta["url"]}" integrity="{meta["sri"]}" crossorigin="anonymous"></script>',
                )
            # Allow CDNs and unsafe-eval in online mode CSP
            # 'unsafe-eval' is required by Tailwind CDN and Babel standalone (if used)
            csp_directives[1] += (
                " 'unsafe-eval' 'self' https://cdn.tailwindcss.com https://unpkg.com"
            )
            csp_directives.append("connect-src *")

        # Replace all nonce placeholders with the actual nonce
        html = html.replace("{{NONCE}}", nonce)

        csp_str = "; ".join(csp_directives) + ";"
        html = html.replace("{{CSP_DIRECTIVES}}", csp_str)

        csp_meta = f'<meta http-equiv="Content-Security-Policy" content="{csp_str}">'
        html = html.replace("{{CSP_META}}", csp_meta)

        # 4. JSON Data Injection
        # Minify JSON for embedding (separators removes extra spaces)
        report_json = json.dumps(self.to_dict(), separators=(",", ":"), cls=ReportEncoder)

        # Security: Escape </ to prevent XSS when embedding JSON in <script> tags
        # even though we primarily use Base64 now, this is a safety fallback.
        report_json = report_json.replace("</", "<\\/")

        # Base64 encode the JSON for secure embedding in a data-attribute
        # This completely avoids XSS from the JSON data
        encoded_json = base64.b64encode(report_json.encode("utf-8")).decode("utf-8")

        if minify:
            # Safer minification: strip leading/trailing whitespace from each line
            # We skip heavy regex-based comment removal as it's dangerous for pre-compiled templates
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
