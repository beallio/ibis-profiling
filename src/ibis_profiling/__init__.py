import ibis
import math
import ibis.expr.datatypes as dt
import ibis.expr.types as ir
from datetime import datetime
from .inspector import DatasetInspector
from .metrics import registry, safe_col
from .planner import QueryPlanner
from .engine import ExecutionEngine
from .report import ProfileReport as InternalProfileReport
from typing import Callable, cast
from concurrent.futures import ThreadPoolExecutor, as_completed


def __getattr__(name):
    if name == "__version__":
        from ._version import get_version

        v = get_version()
        # Cache it in the module's globals for subsequent accesses
        globals()["__version__"] = v
        return v
    raise AttributeError(f"module {__name__} has no attribute {name}")


class Profiler:
    """Orchestrates the profiling process in distinct phases."""

    def __init__(
        self,
        table: ibis.Table,
        minimal: bool = False,
        title: str = "Ibis Profiling Report",
        on_progress: Callable[[int, str | None], None] | None = None,
        correlations: bool | None = None,
        monotonicity: bool | None = None,
        compute_duplicates: bool | None = None,
        cardinality_threshold: int = 20,
        max_interaction_pairs: int = 10,
        correlations_sampling_threshold: int = 1_000_000,
        correlations_sample_size: int = 1_000_000,
        correlations_max_columns: int = 15,
        missing_heatmap_max_columns: int = 15,
        monotonicity_threshold: int = 100_000,
        duplicates_threshold: int = 50_000_000,
        monotonicity_order_by: str | None = None,
        parallel: bool = False,
        pool_size: int = 4,
    ):
        from typing import Any

        self.table = table
        self.minimal = minimal
        self.title = title
        self.on_progress = on_progress
        self.compute_correlations = not minimal if correlations is None else correlations
        self.compute_monotonicity = not minimal if monotonicity is None else monotonicity
        self.explicit_monotonicity = monotonicity is True
        self.compute_duplicates = not minimal if compute_duplicates is None else compute_duplicates
        self.explicit_duplicates = compute_duplicates is True
        self.cardinality_threshold = cardinality_threshold
        self.max_interaction_pairs = max_interaction_pairs
        self.correlations_sampling_threshold = correlations_sampling_threshold
        self.correlations_sample_size = correlations_sample_size
        # Enforce minimum of 2 columns for correlations
        self.correlations_max_columns = max(2, correlations_max_columns)
        self.missing_heatmap_max_columns = max(2, missing_heatmap_max_columns)
        self.monotonicity_threshold = monotonicity_threshold
        self.duplicates_threshold = duplicates_threshold
        self.monotonicity_order_by = monotonicity_order_by
        self.parallel = parallel
        self.pool_size = pool_size

        self.start_time = datetime.now()
        self.inspector = DatasetInspector(table)
        self.planner = QueryPlanner(table, registry)
        self.engine = ExecutionEngine()
        self.executor = ThreadPoolExecutor(max_workers=pool_size) if parallel else None

        self.col_types: dict[str, Any] = self.inspector.get_column_types()
        self.report_data = {
            "analysis": {
                "title": title,
                "date_start": self.start_time.isoformat(),
            },
            "variables": {},
            "table": {},
        }

    def _update_progress(self, inc: int, label: str | None = None):
        if self.on_progress:
            self.on_progress(inc, label)

    def run(self) -> InternalProfileReport:
        """Executes all phases of profiling."""
        try:
            # Start at 0
            self._update_progress(0, "Analyzing dataset...")

            # 1. Global Aggregates (20%)
            self._update_progress(20 if not self.minimal else 30, "Executing global aggregates...")
            global_plan = self.planner.build_global_aggregation()
            raw_results = self.engine.execute(global_plan)

            # 2. Metadata & Initial Report (10%)
            self._update_progress(10, "Metadata analysis...")
            row_count = raw_results["_dataset__row_count"][0] if not raw_results.is_empty() else 0
            mem_size = self.engine.get_storage_size(self.table)
            if mem_size is None:
                mem_size = self.inspector.estimate_memory_size(row_count)

            self.col_types["_dataset"] = {
                "memory_size": mem_size,
                "record_size": mem_size / row_count if row_count > 0 else 0,
            }

            report = InternalProfileReport(raw_results, self.col_types, title=self.title)
            report.analysis["date_start"] = self.start_time.isoformat()

            # 3. Reclassification & Static Analysis (10%)
            self._update_progress(5, "Reclassifying variables...")
            self._reclassify(report)

            self._update_progress(5, "Static analysis...")
            for col_name in report.variables:
                if col_name != "_dataset":
                    report.variables[col_name]["hashable"] = self.inspector.is_hashable(col_name)

            # 4. Duplicates (if not minimal) (10%)
            if self.compute_duplicates:
                n_total = report.table.get("n", 0)
                n_total_int = int(n_total) if isinstance(n_total, (int, float)) else 0

                if n_total_int > self.duplicates_threshold and not self.explicit_duplicates:
                    self._update_progress(10, "Skipping duplicate check for large dataset...")
                    report.analysis.setdefault("warnings", []).append(
                        f"Skipped duplicate check for large dataset ({n_total_int:,} rows). "
                        f"Threshold: {self.duplicates_threshold:,}. Set compute_duplicates=True to force."
                    )
                    report.table["n_distinct_rows"] = "Skipped"
                    report.table["n_duplicates"] = "Skipped"
                    report.table["p_duplicates"] = "Skipped"
                else:
                    self._update_progress(10, "Checking for duplicates...")
                    n_distinct_rows = self.table.distinct().count().execute()
                    report.table["n_distinct_rows"] = n_distinct_rows
                    if isinstance(n_total, (int, float)):
                        report.table["n_duplicates"] = n_total - n_distinct_rows
                        report.table["p_duplicates"] = (
                            (n_total - n_distinct_rows) / n_total if n_total > 0 else 0
                        )
            else:
                if not self.minimal:
                    self._update_progress(10, "Skipping duplicate check...")
                    report.analysis.setdefault("warnings", []).append(
                        "Skipped duplicate check as requested."
                    )
                else:
                    pass

            # 5. Advanced Moments & Histograms (20%)
            self._run_advanced_pass(report)

            # 6. Complex Metrics (15%)
            self._run_complex_pass(report)

            # 7. Correlations (5%)
            if self.compute_correlations:
                self._run_correlations(report)
            elif not self.minimal:
                self._update_progress(5)

            # 8. Monotonicity (5%)
            if self.compute_monotonicity:
                self._run_monotonicity(report)
            elif not self.minimal:
                self._update_progress(5)

            # 9. Samples & Missing Matrix (5%)
            self._run_final_pass(report)

            end_time = datetime.now()
            report.analysis["date_end"] = end_time.isoformat()
            report.analysis["duration"] = (end_time - self.start_time).total_seconds() * 1000

            self._update_progress(0, "Report complete.")
            return report
        finally:
            if self.executor:
                self.executor.shutdown(wait=True)

    def _reclassify(self, report: InternalProfileReport):
        for col_name, stats in report.variables.items():
            if stats.get("type") == "Numeric":
                dtype = self.col_types.get(col_name)
                if isinstance(dtype, dt.Integer):
                    n_distinct = stats.get("n_distinct", 0)
                    if 0 < n_distinct < self.cardinality_threshold:
                        stats["type"] = "Categorical"
                        types_dict = report.table.get("types", {})
                        if isinstance(types_dict, dict) and "Numeric" in types_dict:
                            types_dict["Numeric"] -= 1
                            types_dict["Categorical"] = types_dict.get("Categorical", 0) + 1

    def _run_advanced_pass(self, report: InternalProfileReport):
        self._update_progress(10 if not self.minimal else 20, "Advanced moments calculation...")
        second_pass_aggs = []
        histogram_plans = []
        nbins = 20
        plottable_cols = [
            c for c, s in report.variables.items() if s.get("type") in ["Numeric", "DateTime"]
        ]

        for col_name in plottable_cols:
            stats = report.variables[col_name]
            v_type = stats.get("type")
            col = self.table[col_name]
            safe_c = safe_col(col)

            if v_type == "DateTime":
                col = col.epoch_seconds().cast("float64")
                v_min_raw = stats.get("min")
                v_max_raw = stats.get("max")

                def to_timestamp(val):
                    if val is None:
                        return None
                    # 1. Handle string/bytes (fallback to isoparse)
                    if isinstance(val, (str, bytes)):
                        import dateutil.parser

                        try:
                            return dateutil.parser.isoparse(val).timestamp()
                        except Exception:
                            return None
                    # 2. Handle datetime objects
                    from datetime import datetime, date

                    if isinstance(val, datetime):
                        return val.timestamp()
                    if isinstance(val, date):
                        return datetime.combine(val, datetime.min.time()).timestamp()
                    # 3. Handle pandas/numpy/others if available
                    if hasattr(val, "timestamp") and callable(val.timestamp):
                        try:
                            return val.timestamp()
                        except Exception:
                            pass
                    # 4. Handle numpy.datetime64 specifically if it doesn't have .timestamp()
                    if hasattr(val, "astype") and "datetime64" in str(getattr(val, "dtype", "")):
                        import numpy as np

                        try:
                            return val.astype("datetime64[s]").astype(np.int64)
                        except Exception:
                            pass
                    return None

                v_min = to_timestamp(v_min_raw)
                v_max = to_timestamp(v_max_raw)

                if v_min_raw and v_max_raw and (v_min is None or v_max is None):
                    report.analysis.setdefault("warnings", []).append(
                        f"Histogram failed for {col_name}: Could not convert min/max "
                        f"({v_min_raw}/{v_max_raw}) to timestamp."
                    )
            else:
                mean = stats.get("mean")
                std = stats.get("std")
                v_min = stats.get("min")
                v_max = stats.get("max")

                if not self.minimal and mean is not None and std is not None and std > 0:
                    skew_expr = ((safe_c - mean) / std).pow(3).mean().name(f"{col_name}__skewness")
                    second_pass_aggs.append(skew_expr)
                    mad_expr = (safe_c - mean).abs().mean().name(f"{col_name}__mad")
                    second_pass_aggs.append(mad_expr)

                col = safe_c

            if v_min is not None and v_max is not None and v_max > v_min:
                range_size = v_max - v_min
                bin_expr = (
                    (((col - v_min) / range_size) * nbins).floor().clip(lower=0, upper=nbins - 1)
                )
                hist_plan = bin_expr.value_counts()
                histogram_plans.append((col_name, hist_plan, v_min, v_max, nbins))

        if second_pass_aggs:
            results = self.table.aggregate(second_pass_aggs).to_pyarrow().to_pydict()
            for k, v in results.items():
                parts = k.rsplit("__", 1)
                report.add_metric(parts[0], parts[1], v[0])

        hist_inc = (
            (10 if not self.minimal else 10) / len(histogram_plans) if histogram_plans else 10
        )

        def run_hist(p):
            col_name, plan, v_min, v_max, nbins = p
            try:
                res = plan.execute()
                return col_name, res, v_min, v_max, nbins, None
            except Exception as exc:
                return col_name, None, v_min, v_max, nbins, exc

        if self.executor and histogram_plans:
            futures = [self.executor.submit(run_hist, p) for p in histogram_plans]
            results = [f.result() for f in as_completed(futures)]
        else:
            results = [run_hist(p) for p in histogram_plans]

        for col_name, res, v_min, v_max, nbins, exc in results:
            self._update_progress(int(hist_inc), f"Processing histogram for {col_name}...")
            if exc:
                report.analysis.setdefault("warnings", []).append(
                    f"Histogram failed for {col_name}: {exc}"
                )
                continue
            if res is None:
                continue

            try:
                c_key = "count" if "count" in res.columns else res.columns[1]
                l_key = res.columns[0]
                counts_dict = {
                    int(k): v
                    for k, v in zip(res[l_key], res[c_key])
                    if k is not None and not (isinstance(k, float) and math.isnan(k))
                }
                report.add_metric(
                    col_name,
                    "numeric_histogram",
                    {"counts": counts_dict, "min": v_min, "max": v_max, "nbins": nbins},
                )
            except Exception as e:
                report.analysis.setdefault("warnings", []).append(
                    f"Histogram processing failed for {col_name}: {e}"
                )

    def _run_complex_pass(self, report: InternalProfileReport):
        final_types = {c: s.get("type") for c, s in report.variables.items()}
        complex_plans = self.planner.build_complex_metrics(
            override_types=final_types, variables_metadata=report.variables
        )

        value_aggs = []
        table_plans = []

        for col_name, metric_name, expr, hint in complex_plans:
            if hint == "Value":
                if isinstance(expr, ir.Value):
                    value_aggs.append(expr.name(f"{col_name}__{metric_name}"))
                else:
                    table_plans.append((col_name, metric_name, expr))
            else:
                table_plans.append((col_name, metric_name, expr))

        # 1. Execute batched scalar metrics
        if value_aggs:
            self._update_progress(5, "Calculating batched scalar metrics...")
            try:
                results = self.table.aggregate(value_aggs).to_pyarrow().to_pydict()
                for k, v in results.items():
                    parts = k.rsplit("__", 1)
                    report.add_metric(parts[0], parts[1], v[0])
            except Exception as exc:
                report.analysis.setdefault("warnings", []).append(
                    f"Batched complex metrics failed: {exc}. Falling back to individual queries."
                )
                # Sequential fallback for scalars
                for col_name, metric_name, expr, hint in complex_plans:
                    if hint == "Value":
                        try:
                            val = expr.to_pyarrow().as_py()
                            report.add_metric(col_name, metric_name, val)
                        except Exception:
                            continue
        else:
            # If no batched metrics, move the 5% to the next section
            self._update_progress(0, "Skipping batched metrics...")

        # 2. Execute Table metrics in parallel if executor is present
        # Total complex pass is 15%. If batched was 5, we have 10 left.
        # If batched was 0, we have 15 left.
        total_remaining = 10 if value_aggs else 15
        inc = total_remaining / len(table_plans) if table_plans else total_remaining

        def run_table_plan(p):
            col_name, metric_name, expr = p
            try:
                if isinstance(expr, ir.Table):
                    val = expr.to_pyarrow().to_pydict()
                else:
                    val = expr.to_pyarrow().as_py()
                return col_name, metric_name, val, None
            except Exception as exc:
                return col_name, metric_name, None, exc

        if self.executor and table_plans:
            futures = [self.executor.submit(run_table_plan, p) for p in table_plans]
            results = [f.result() for f in as_completed(futures)]
        else:
            results = [run_table_plan(p) for p in table_plans]

        processed_inc = 0
        for i, (col_name, metric_name, val, exc) in enumerate(results):
            # Calculate increment to ensure we hit exactly total_remaining
            current_total = int((i + 1) * inc)
            this_inc = current_total - processed_inc
            processed_inc = current_total

            self._update_progress(this_inc, f"Processing {metric_name} for {col_name}...")
            if exc:
                report.analysis.setdefault("warnings", []).append(
                    f"{metric_name} failed for {col_name}: {exc}"
                )
            elif val is not None:
                report.add_metric(col_name, metric_name, val)

        # Ensure any leftover due to rounding is accounted for
        if processed_inc < total_remaining:
            self._update_progress(total_remaining - processed_inc)

    def _run_correlations(self, report: InternalProfileReport):
        self._update_progress(5, "Correlations pass...")
        from .report.model.correlations import CorrelationEngine

        numeric_cols = []
        for c, s in report.variables.items():
            if s.get("type") == "Numeric":
                numeric_cols.append(c)
            elif s.get("type") in ["Boolean", "Categorical"]:
                dtype = self.col_types.get(c)
                if isinstance(dtype, (dt.Integer, dt.Boolean)):
                    numeric_cols.append(c)

        if len(numeric_cols) >= 2:
            res = CorrelationEngine.compute_all(
                self.table,
                report.variables,
                row_count=cast(int | None, report.table.get("n")),
                sampling_threshold=self.correlations_sampling_threshold,
                sample_size=self.correlations_sample_size,
                max_columns=self.correlations_max_columns,
            )
            meta = res.get("_metadata", {})
            if meta.get("truncated"):
                report.analysis.setdefault("warnings", []).append(
                    f"Correlations truncated to top {meta['limit']} columns (out of {meta['original_count']}) "
                    "to ensure performance."
                )
            report.correlations = res

    def _run_monotonicity(self, report: InternalProfileReport):
        self._update_progress(5, "Monotonicity checks...")
        n_val = report.table.get("n", 0)
        row_count = int(n_val) if isinstance(n_val, (int, float)) else 0

        if row_count > self.monotonicity_threshold and not self.explicit_monotonicity:
            report.analysis.setdefault("warnings", []).append(
                f"Skipped monotonicity checks for large dataset ({row_count:,} rows). "
                f"Threshold: {self.monotonicity_threshold:,} rows."
            )
            for col_name, stats in report.variables.items():
                if stats.get("type") == "Numeric":
                    report.add_metric(col_name, "monotonic_increasing", "Skipped")
                    report.add_metric(col_name, "monotonic_decreasing", "Skipped")
            return

        numeric_cols = [c for c, s in report.variables.items() if s.get("type") == "Numeric"]
        if not self.monotonicity_order_by:
            report.analysis.setdefault("warnings", []).append(
                "Skipped monotonicity checks. Monotonicity requires a deterministic 'monotonicity_order_by' column to be reliable."
            )
            for col_name in numeric_cols:
                report.add_metric(col_name, "monotonic_increasing", "Skipped")
                report.add_metric(col_name, "monotonic_decreasing", "Skipped")
            return

        if self.monotonicity_order_by not in self.table.schema():
            report.analysis.setdefault("warnings", []).append(
                f"Skipped monotonicity checks. The requested 'monotonicity_order_by' column '{self.monotonicity_order_by}' was not found in the table schema."
            )
            for col_name in numeric_cols:
                report.add_metric(col_name, "monotonic_increasing", "Skipped")
                report.add_metric(col_name, "monotonic_decreasing", "Skipped")
            return

        mono_checks = []
        # Use order_by column for deterministic window
        win = ibis.window(order_by=self.monotonicity_order_by)

        for col_name in numeric_cols:
            col = self.table[col_name]
            prev = col.lag().over(win)
            mono_checks.append(((col >= prev) | prev.isnull()).name(f"inc_{col_name}"))
            mono_checks.append(((col <= prev) | prev.isnull()).name(f"dec_{col_name}"))

        if mono_checks:
            check_table = self.table.mutate(*mono_checks)
            final_aggs = []
            for col_name in numeric_cols:
                final_aggs.append(
                    check_table[f"inc_{col_name}"].all().name(f"{col_name}__monotonic_increasing")
                )
                final_aggs.append(
                    check_table[f"dec_{col_name}"].all().name(f"{col_name}__monotonic_decreasing")
                )
            results = check_table.aggregate(final_aggs).to_pyarrow().to_pydict()
            for k, v in results.items():
                parts = k.rsplit("__", 1)
                report.add_metric(parts[0], parts[1], v[0])

    def _run_final_pass(self, report: InternalProfileReport):
        self._update_progress(2, "Capturing samples...")
        head_sample = self.table.head(10).to_pyarrow().to_pydict()
        report.add_metric("_dataset", "head", head_sample)
        if not self.minimal:
            self._update_progress(2, "Missing values matrix...")
            from .report.model.missing import MissingEngine

            report.missing = MissingEngine.compute(
                self.table, report.variables, max_heatmap_columns=self.missing_heatmap_max_columns
            )
            # Record truncation warning if applicable
            m_meta = report.missing.get("heatmap", {}).get("matrix", {}).get("_metadata", {})
            if m_meta.get("truncated"):
                report.analysis.setdefault("warnings", []).append(
                    f"Missingness heatmap truncated to top {m_meta['limit']} columns "
                    f"(out of {m_meta['original_count']}) with most missing values."
                )
            self._update_progress(1, "Pairwise interactions...")
            from .report.model.interactions import InteractionEngine

            n_total = report.table.get("n", None)
            if not isinstance(n_total, int):
                n_total = None

            report.interactions = InteractionEngine.compute(
                self.table,
                report.variables,
                row_count=n_total,
                max_interaction_pairs=self.max_interaction_pairs,
                correlations=report.correlations,
            )
        else:
            self._update_progress(3)


def profile(
    table: ibis.Table,
    minimal: bool = False,
    title: str = "Ibis Profiling Report",
    on_progress: Callable[[int, str | None], None] | None = None,
    correlations: bool | None = None,
    monotonicity: bool | None = None,
    compute_duplicates: bool | None = None,
    cardinality_threshold: int = 20,
    max_interaction_pairs: int = 10,
    correlations_sampling_threshold: int = 1_000_000,
    correlations_sample_size: int = 1_000_000,
    correlations_max_columns: int = 15,
    missing_heatmap_max_columns: int = 15,
    monotonicity_threshold: int = 100_000,
    duplicates_threshold: int = 50_000_000,
    monotonicity_order_by: str | None = None,
    parallel: bool = False,
    pool_size: int = 4,
) -> InternalProfileReport:
    """Main entrypoint for profiling an Ibis table."""
    profiler = Profiler(
        table,
        minimal=minimal,
        title=title,
        on_progress=on_progress,
        correlations=correlations,
        monotonicity=monotonicity,
        compute_duplicates=compute_duplicates,
        cardinality_threshold=cardinality_threshold,
        max_interaction_pairs=max_interaction_pairs,
        correlations_sampling_threshold=correlations_sampling_threshold,
        correlations_sample_size=correlations_sample_size,
        correlations_max_columns=correlations_max_columns,
        missing_heatmap_max_columns=missing_heatmap_max_columns,
        monotonicity_threshold=monotonicity_threshold,
        duplicates_threshold=duplicates_threshold,
        monotonicity_order_by=monotonicity_order_by,
        parallel=parallel,
        pool_size=pool_size,
    )
    return profiler.run()


def profile_excel(path: str, **kwargs) -> InternalProfileReport:
    """Convenience function to profile an Excel file."""
    return InternalProfileReport.from_excel(path, **kwargs)


class ProfileReport:
    """
    Compatibility wrapper to mimic ydata-profiling API.
    """

    def __init__(
        self,
        table: ibis.Table,
        minimal: bool = False,
        on_progress: Callable[[int, str | None], None] | None = None,
        correlations: bool | None = None,
        monotonicity: bool | None = None,
        compute_duplicates: bool | None = None,
        monotonicity_threshold: int = 100_000,
        duplicates_threshold: int = 50_000_000,
        correlations_max_columns: int = 15,
        missing_heatmap_max_columns: int = 15,
        monotonicity_order_by: str | None = None,
        **kwargs,
    ):
        self.table = table
        self.minimal = minimal
        self.on_progress = on_progress
        self.correlations = correlations
        self.monotonicity = monotonicity
        self.compute_duplicates = compute_duplicates
        self.monotonicity_threshold = monotonicity_threshold
        self.duplicates_threshold = duplicates_threshold
        self.correlations_max_columns = correlations_max_columns
        self.missing_heatmap_max_columns = missing_heatmap_max_columns
        self.monotonicity_order_by = monotonicity_order_by
        self.kwargs = kwargs

        title = kwargs.get("title", "Ibis Profiling Report")
        self._report = profile(
            table,
            minimal=minimal,
            title=title,
            on_progress=on_progress,
            correlations=correlations,
            monotonicity=monotonicity,
            compute_duplicates=compute_duplicates,
            cardinality_threshold=kwargs.get("cardinality_threshold", 20),
            monotonicity_threshold=monotonicity_threshold,
            duplicates_threshold=duplicates_threshold,
            correlations_max_columns=correlations_max_columns,
            missing_heatmap_max_columns=missing_heatmap_max_columns,
            monotonicity_order_by=monotonicity_order_by,
            max_interaction_pairs=kwargs.get("max_interaction_pairs", 10),
            correlations_sampling_threshold=kwargs.get(
                "correlations_sampling_threshold", 1_000_000
            ),
            correlations_sample_size=kwargs.get("correlations_sample_size", 1_000_000),
            parallel=kwargs.get("parallel", False),
            pool_size=kwargs.get("pool_size", 4),
        )

    @classmethod
    def from_excel(cls, path: str, **kwargs) -> "ProfileReport":
        """Compatibility method to mimic ydata-profiling from_excel."""
        instance = cls.__new__(cls)
        instance._report = profile_excel(path, **kwargs)
        return instance

    def to_file(self, output_file: str, theme: str = "default", minify: bool = True):
        return self._report.to_file(output_file, theme=theme, minify=minify)

    def to_json(self) -> str:
        return self._report.to_json()

    def to_dict(self) -> dict:
        return self._report.to_dict()

    def get_description(self) -> dict:
        return self._report.get_description()

    def to_html(self, theme: str = "default", minify: bool = True) -> str:
        return self._report.to_html(theme=theme, minify=minify)


__all__ = ["profile", "registry", "ProfileReport", "profile_excel", "__version__"]
