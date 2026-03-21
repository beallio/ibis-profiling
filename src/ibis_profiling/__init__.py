import ibis
import ibis.expr.datatypes as dt
import ibis.expr.types as ir
from datetime import datetime
from .inspector import DatasetInspector
from .metrics import registry, safe_col
from .planner import QueryPlanner
from .engine import ExecutionEngine
from .report import ProfileReport as InternalProfileReport


from typing import Callable


def profile(
    table: ibis.Table,
    minimal: bool = False,
    title: str = "Ibis Profiling Report",
    on_progress: Callable[[int, str | None], None] | None = None,
) -> InternalProfileReport:
    """
    Main entrypoint for profiling an Ibis table.

    This function:
    1. Inspects the table schema.
    2. Plans a minimal set of batched aggregation queries.
    3. Executes the queries in the backend.
    4. Formats the results into a structured report.
    """
    start_time = datetime.now()

    def update_progress(inc, label=None):
        if on_progress:
            on_progress(inc, label)

    update_progress(0, "Analyzing dataset...")
    inspector = DatasetInspector(table)
    planner = QueryPlanner(table, registry)
    engine = ExecutionEngine()

    # 1. Generate and execute simple aggregates (1 pass)
    update_progress(15 if not minimal else 25, "Executing global aggregates...")
    global_plan = planner.build_global_aggregation()
    raw_results = engine.execute(global_plan)

    # 2. Collect Table Metadata (Memory, etc.)
    update_progress(5 if not minimal else 10, "Metadata analysis...")
    row_count = raw_results["_dataset__row_count"][0] if not raw_results.is_empty() else 0
    mem_size = engine.get_storage_size(table)
    if mem_size is None:
        mem_size = inspector.estimate_memory_size(row_count)

    col_types = inspector.get_column_types()
    # Inject dataset metadata into schema for the Report model to pick up
    # Use a cast or temporary storage if ty complains about dict[str, dt.DataType]
    # In this case, we'll use the dict's flexibility but we might need to cast for ty
    col_types["_dataset"] = {  # type: ignore
        "memory_size": mem_size,
        "record_size": mem_size / row_count if row_count > 0 else 0,
    }

    # 3. Build base report
    report = InternalProfileReport(raw_results, col_types, title=title)
    report.analysis["date_start"] = start_time.isoformat()

    # 4. Low-cardinality Reclassification (Heuristic)
    update_progress(0, "Reclassifying variables...")
    # NOTE: We only reclassify INTEGERS to Categorical. Floats/Decimals stay Numeric
    # even if low cardinality (to keep precise stats and avoid breaking tests).
    CARDINALITY_THRESHOLD = 20
    for col_name, stats in report.variables.items():
        if stats.get("type") == "Numeric":
            dtype = col_types.get(col_name)
            if isinstance(dtype, dt.Integer):
                n_distinct = stats.get("n_distinct", 0)
                if 0 < n_distinct < CARDINALITY_THRESHOLD:
                    stats["type"] = "Categorical"
                    # Update table-level type counts
                    types_dict = report.table.get("types", {})
                    if isinstance(types_dict, dict) and "Numeric" in types_dict:
                        types_dict["Numeric"] -= 1
                        types_dict["Categorical"] = types_dict.get("Categorical", 0) + 1

    # 5. Inject column-level static metadata (hashable)
    update_progress(5 if not minimal else 10, "Static analysis...")
    for col_name in report.variables:
        if col_name != "_dataset":
            report.variables[col_name]["hashable"] = inspector.is_hashable(col_name)

    # 5. Handle dataset-wide distinct count (Duplicates)
    # We do this separately to avoid IntegrityErrors in the global batch
    if not minimal:
        update_progress(5, "Checking for duplicates...")
        n_distinct_rows = table.distinct().count().execute()
        report.table["n_distinct_rows"] = n_distinct_rows
        n_total = report.table.get("n", 0)
        if isinstance(n_total, (int, float)):
            report.table["n_duplicates"] = n_total - n_distinct_rows
            report.table["p_duplicates"] = (
                (n_total - n_distinct_rows) / n_total if n_total > 0 else 0
            )

    # 4. Handle advanced moments (Skewness, MAD) and Histograms in a second pass
    # We use mean/std from pass 1 to avoid nesting issues
    second_pass_aggs = []
    histogram_plans = []
    nbins = 20
    # Include DateTime for histograms (epoch conversion)
    plottable_cols = [
        c for c, s in report.variables.items() if s.get("type") in ["Numeric", "DateTime"]
    ]

    update_progress(5 if not minimal else 10, "Advanced moments calculation...")
    for col_name in plottable_cols:
        stats = report.variables[col_name]
        v_type = stats.get("type")
        col = table[col_name]
        safe_c = safe_col(col)

        # For DateTime, we work with epoch seconds
        if v_type == "DateTime":
            col = col.epoch_seconds().cast("float64")
            v_min_raw = stats.get("min")
            v_max_raw = stats.get("max")
            if v_min_raw and v_max_raw:
                import dateutil.parser

                try:
                    v_min = dateutil.parser.isoparse(v_min_raw).timestamp()
                    v_max = dateutil.parser.isoparse(v_max_raw).timestamp()
                except Exception:
                    v_min, v_max = None, None
            else:
                v_min, v_max = None, None
        else:
            mean = stats.get("mean")
            std = stats.get("std")
            v_min = stats.get("min")
            v_max = stats.get("max")

            # Skewness (only if not minimal)
            if not minimal and mean is not None and std is not None and std > 0:
                skew_expr = ((safe_c - mean) / std).pow(3).mean().name(f"{col_name}__skewness")
                second_pass_aggs.append(skew_expr)

            # MAD (only if not minimal)
            if not minimal and mean is not None:
                mad_expr = (safe_c - mean).abs().mean().name(f"{col_name}__mad")
                second_pass_aggs.append(mad_expr)

            # Important: use safe_c for histogram calculation too
            col = safe_c

        # Proper Histogram (Bucket Pass) - ALWAYS computed
        if v_min is not None and v_max is not None and v_max > v_min:
            range_size = v_max - v_min
            bin_expr = (((col - v_min) / range_size) * nbins).floor().clip(lower=0, upper=nbins - 1)
            hist_plan = bin_expr.value_counts()
            histogram_plans.append((col_name, hist_plan, v_min, v_max))

    if second_pass_aggs:
        results = table.aggregate(second_pass_aggs).to_pyarrow().to_pydict()
        for k, v in results.items():
            parts = k.split("__")
            c_name, m_name = parts[0], parts[1]
            report.add_metric(c_name, m_name, v[0])

    # Execute histograms
    hist_count = len(histogram_plans)
    hist_inc = (
        (15 if not minimal else 20) / hist_count if hist_count > 0 else (15 if not minimal else 20)
    )
    for col_name, plan, v_min, v_max in histogram_plans:
        update_progress(hist_inc, f"Calculating histogram for {col_name}...")
        # Skip if it was reclassified to Categorical (handled by top_values)
        if report.variables[col_name].get("type") == "Categorical":
            continue

        try:
            res = plan.execute()
            # Find columns
            c_key = "count" if "count" in res.columns else res.columns[1]
            l_key = res.columns[0]

            # Filter out None/NaN and ensure int keys
            counts_dict = {}
            import math

            for k, v in zip(res[l_key], res[c_key]):
                if k is not None and not (isinstance(k, float) and math.isnan(k)):
                    counts_dict[int(k)] = v

            report.add_metric(
                col_name,
                "numeric_histogram",
                {"counts": counts_dict, "min": v_min, "max": v_max, "nbins": nbins},
            )
        except Exception as exc:
            report.analysis.setdefault("warnings", []).append(
                f"Histogram failed for {col_name}: {exc}"
            )

    # 4. Handle complex metrics (e.g. n_unique, top_values)
    final_types = {c: s.get("type") for c, s in report.variables.items()}
    complex_plans = planner.build_complex_metrics(override_types=final_types)
    complex_count = len(complex_plans)
    complex_inc = (
        (15 if not minimal else 15) / complex_count
        if complex_count > 0
        else (15 if not minimal else 15)
    )
    for col_name, metric_name, expr in complex_plans:
        update_progress(complex_inc, f"Calculating {metric_name} for {col_name}...")
        if isinstance(expr, ir.Table):
            # For table-valued metrics like top_values
            val = expr.to_pyarrow().to_pydict()
        else:
            # For scalar-valued metrics like n_unique
            val = expr.to_pyarrow().as_py()
        report.add_metric(col_name, metric_name, val)

    # 4. Handle Correlations
    if not minimal:
        update_progress(10, "Correlations pass...")
        from .report.model.correlations import CorrelationEngine

        # Use all numeric types PLUS booleans and reclassified integers for correlations
        # Spearman can technically work on ranks of anything, but Pearson needs numeric-like
        numeric_cols = []
        for c, s in report.variables.items():
            if s.get("type") == "Numeric":
                numeric_cols.append(c)
            elif s.get("type") in ["Boolean", "Categorical"]:
                # Only include categoricals that were originally integers (standard profiling practice)
                dtype = col_types.get(c)
                if isinstance(dtype, (dt.Integer, dt.Boolean)):
                    numeric_cols.append(c)

        if len(numeric_cols) >= 2:
            # 4a. Pearson (Simple Aggregates)
            corr_results = CorrelationEngine._compute_pearson(table, numeric_cols)
            flat_exprs = []
            for i, row in enumerate(corr_results["matrix"]):
                for j, item in enumerate(row):
                    if isinstance(item, ir.Scalar):
                        flat_exprs.append(item.name(f"corr_pearson_{i}_{j}"))

            if flat_exprs:
                executed_vals = table.aggregate(flat_exprs).to_pyarrow().to_pydict()
                final_matrix = []
                val_idx = 0
                for i, row in enumerate(corr_results["matrix"]):
                    new_row = []
                    for j, item in enumerate(row):
                        if i == j:
                            new_row.append(1.0)
                        else:
                            key = list(executed_vals.keys())[val_idx]
                            new_row.append(executed_vals[key][0])
                            val_idx += 1
                    final_matrix.append(new_row)
                report.correlations["pearson"] = {"columns": numeric_cols, "matrix": final_matrix}

            # 4b. Spearman (Rank Pass)
            spearman_meta = CorrelationEngine._compute_spearman(table, numeric_cols)
            rank_exprs = [spearman_meta["rank_exprs"][c].name(f"rank_{c}") for c in numeric_cols]
            # Create a CTE-like table with ranks
            rank_table = table.mutate(*rank_exprs)

            flat_spearman = []
            for i, c1 in enumerate(numeric_cols):
                for j, c2 in enumerate(numeric_cols):
                    if i < j:
                        r1 = rank_table[f"rank_{c1}"]
                        r2 = rank_table[f"rank_{c2}"]
                        # Pearson on Ranks
                        expr = r1.cov(r2, how="pop") / (r1.std(how="pop") * r2.std(how="pop"))
                        flat_spearman.append(expr.name(f"corr_spearman_{i}_{j}"))

            if flat_spearman:
                executed_vals = rank_table.aggregate(flat_spearman).to_pyarrow().to_pydict()
                final_matrix = [[1.0 for _ in numeric_cols] for _ in numeric_cols]
                val_idx = 0
                for i in range(len(numeric_cols)):
                    for j in range(len(numeric_cols)):
                        if i < j:
                            key = list(executed_vals.keys())[val_idx]
                            val = executed_vals[key][0]
                            final_matrix[i][j] = val
                            final_matrix[j][i] = val
                            val_idx += 1
                report.correlations["spearman"] = {"columns": numeric_cols, "matrix": final_matrix}

    # 5. Handle Monotonicity and other column-wise complex checks
    if not minimal:
        update_progress(5, "Monotonicity checks...")
        numeric_cols = [c for c, s in report.variables.items() if s.get("type") == "Numeric"]
        # Monotonicity check requires a window pass
        # We must perform the comparison IN the window pass (mutate) then aggregate
        mono_checks = []
        for col_name in numeric_cols:
            col = table[col_name]
            prev = col.lag().over(ibis.window())
            mono_checks.append(((col >= prev) | prev.isnull()).name(f"inc_{col_name}"))
            mono_checks.append(((col <= prev) | prev.isnull()).name(f"dec_{col_name}"))

        if mono_checks:
            check_table = table.mutate(*mono_checks)
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
                parts = k.split("__")
                c_name, m_name = parts[0], parts[1]
                report.add_metric(c_name, m_name, v[0])

    # 6. Capture Samples (Head)
    update_progress(5 if not minimal else 10, "Capturing samples...")
    # Note: Ibis doesn't have a reliable cross-backend 'tail' without an order key.
    # We'll just capture the head for now.
    head_sample = table.head(10).to_pyarrow().to_pydict()
    report.add_metric("_dataset", "head", head_sample)

    # 6. Missing Values (Matrix/Heatmap)
    if not minimal:
        update_progress(5, "Missing values matrix...")
        from .report.model.missing import MissingEngine

        report.missing = MissingEngine.compute(table, report.variables)

    # 7. Handle Pairwise Interactions (Scatter Plots)
    if not minimal:
        update_progress(10, "Pairwise interactions...")
        from .report.model.interactions import InteractionEngine

        report.interactions = InteractionEngine.compute(table, report.variables)

    end_time = datetime.now()
    report.analysis["date_end"] = end_time.isoformat()
    report.analysis["duration"] = (end_time - start_time).total_seconds() * 1000

    # Final tick to 100
    update_progress(0, "Report complete.")
    return report


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
        **kwargs,
    ):
        title = kwargs.get("title", "Ibis Profiling Report")
        self._report = profile(table, minimal=minimal, title=title, on_progress=on_progress)

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


__all__ = ["profile", "registry", "ProfileReport", "profile_excel"]
