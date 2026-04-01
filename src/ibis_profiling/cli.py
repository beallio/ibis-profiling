import click
import ibis
import os
import sys
from ibis_profiling import ProfileReport, __version__


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__, prog_name="ibis-profiling")
@click.option(
    "--file-path",
    "-f",
    required=True,
    help="Path to the input file (CSV, Parquet, Excel).",
)
@click.option(
    "--output",
    "-o",
    default="report.html",
    show_default=True,
    help="Path to the output report file.",
)
@click.option(
    "--title",
    "-t",
    default="Ibis Profiling Report",
    show_default=True,
    help="Title of the report.",
)
@click.option("--minimal", is_flag=True, help="Generate a minimal report with fewer metrics.")
@click.option(
    "--correlations/--no-correlations",
    default=None,
    help="Explicitly enable or disable correlations calculation.",
)
@click.option(
    "--monotonicity/--no-monotonicity",
    default=None,
    help="Explicitly enable or disable monotonicity checks.",
)
@click.option(
    "--duplicates/--no-duplicates",
    default=None,
    help="Explicitly enable or disable duplicate row checks.",
)
@click.option(
    "--monotonicity-threshold",
    type=int,
    default=100_000,
    show_default=True,
    help="Row count threshold above which monotonicity is skipped.",
)
@click.option(
    "--duplicates-threshold",
    type=int,
    default=50_000_000,
    show_default=True,
    help="Row count threshold above which duplicate check is skipped.",
)
@click.option(
    "--n-unique-threshold",
    type=int,
    default=50_000_000,
    show_default=True,
    help="Row count/cardinality threshold above which n_unique is skipped.",
)
@click.option(
    "--correlations-max-columns",
    type=click.IntRange(min=2),
    default=15,
    show_default=True,
    help="Maximum number of columns to include in correlation matrix (min 2).",
)
@click.option(
    "--missing-heatmap-max-columns",
    type=click.IntRange(min=2),
    default=15,
    show_default=True,
    help="Maximum number of columns to include in missingness heatmap (min 2).",
)
@click.option(
    "--missing-matrix-max-columns",
    type=click.IntRange(min=2),
    default=50,
    show_default=True,
    help="Maximum number of columns to include in missingness matrix (min 2).",
)
@click.option(
    "--monotonicity-order-by",
    type=str,
    help="Column name to order by for monotonicity checks.",
)
@click.option(
    "--global-batch-size",
    type=int,
    default=500,
    show_default=True,
    help="Maximum number of metrics to compute in a single global aggregate query.",
)
@click.option(
    "--theme",
    type=click.Choice(["default", "ydata-like"]),
    default="default",
    show_default=True,
    help="Report theme (HTML only).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["html", "json"]),
    help="Force output format (overrides extension).",
)
@click.option(
    "--offline/--online",
    default=True,
    show_default=True,
    help="Whether to bundle all JS/CSS assets in the HTML for offline viewing.",
)
@click.option("--debug", is_flag=True, help="Print detailed performance information.")
def main(
    file_path,
    output,
    title,
    minimal,
    correlations,
    monotonicity,
    duplicates,
    monotonicity_threshold,
    duplicates_threshold,
    n_unique_threshold,
    correlations_max_columns,
    missing_heatmap_max_columns,
    missing_matrix_max_columns,
    monotonicity_order_by,
    global_batch_size,
    theme,
    output_format,
    offline,
    debug,
):
    """
    Ultra-high-performance data profiling natively for Ibis.

    This tool reads a dataset (CSV, Parquet, or Excel) and generates a
    comprehensive profiling report in HTML or JSON format.
    """
    if not os.path.exists(file_path):
        click.echo(f"Error: File not found: {file_path}", err=True)
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()

    try:
        report = None
        table = None

        if ext in [".xlsx", ".xls"]:
            click.echo(f"Loading Excel file: {file_path}...")
        elif ext == ".parquet":
            click.echo(f"Loading Parquet file: {file_path}...")
            table = ibis.read_parquet(file_path)
        elif ext == ".csv":
            click.echo(f"Loading CSV file: {file_path}...")
            table = ibis.read_csv(file_path)
        else:
            try:
                click.echo(f"Attempting to load {file_path} as Parquet...")
                table = ibis.read_parquet(file_path)
            except Exception:
                click.echo(f"Attempting to load {file_path} as CSV...")
                table = ibis.read_csv(file_path)

        with click.progressbar(length=100, label="Profiling data") as bar:

            def on_progress(inc, label=None):
                if label:
                    bar.label = f"Profiling: {label}"
                bar.update(inc)

            profile_kwargs = dict(
                title=title,
                minimal=minimal,
                on_progress=on_progress,
                correlations=correlations,
                monotonicity=monotonicity,
                compute_duplicates=duplicates,
                monotonicity_threshold=monotonicity_threshold,
                duplicates_threshold=duplicates_threshold,
                n_unique_threshold=n_unique_threshold,
                correlations_max_columns=correlations_max_columns,
                missing_heatmap_max_columns=missing_heatmap_max_columns,
                missing_matrix_max_columns=missing_matrix_max_columns,
                monotonicity_order_by=monotonicity_order_by,
                global_batch_size=global_batch_size,
            )

            if ext in [".xlsx", ".xls"]:
                report = ProfileReport.from_excel(file_path, **profile_kwargs)
            else:
                assert table is not None
                report = ProfileReport(
                    table,
                    title=title,
                    minimal=minimal,
                    on_progress=on_progress,
                    correlations=correlations,
                    monotonicity=monotonicity,
                    compute_duplicates=duplicates,
                    monotonicity_threshold=monotonicity_threshold,
                    duplicates_threshold=duplicates_threshold,
                    n_unique_threshold=n_unique_threshold,
                    correlations_max_columns=correlations_max_columns,
                    missing_heatmap_max_columns=missing_heatmap_max_columns,
                    missing_matrix_max_columns=missing_matrix_max_columns,
                    monotonicity_order_by=monotonicity_order_by,
                    global_batch_size=global_batch_size,
                )

        if debug:
            perf = report.get_description()["analysis"].get("performance", {})
            if perf:
                click.echo("\n--- Performance Debug Summary ---")
                # Sort by duration descending
                sorted_perf = sorted(perf.items(), key=lambda x: x[1], reverse=True)
                for phase, duration in sorted_perf:
                    click.echo(f"{phase:25}: {duration:8.2f} ms")
                click.echo("---------------------------------\n")

        if not output_format:
            output_format = "json" if output.endswith(".json") else "html"

        click.echo(f"Generating {output_format.upper()} report...")
        if output_format == "json":
            content = report.to_json()
        else:
            content = report.to_html(theme=theme, offline=offline)

        with open(output, "w") as f:
            f.write(content)

        click.echo(f"Report successfully generated: {output}")

    except Exception as e:
        click.echo(f"Error during profiling: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
