import click
import ibis
import os
import sys
from ibis_profiling import ProfileReport


@click.command()
@click.option(
    "--file-path", "-f", required=True, help="Path to the input file (CSV, Parquet, Excel)."
)
@click.option("--output", "-o", default="report.html", help="Path to the output report file.")
@click.option("--title", "-t", default="Ibis Profiling Report", help="Title of the report.")
@click.option("--minimal", is_flag=True, help="Generate a minimal report.")
@click.option(
    "--theme",
    type=click.Choice(["default", "ydata-like"]),
    default="default",
    help="Report theme (HTML only).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["html", "json"]),
    help="Force output format (overrides extension).",
)
def main(file_path, output, title, minimal, theme, output_format):
    """Profile a dataset using Ibis and generate a report."""
    if not os.path.exists(file_path):
        click.echo(f"Error: File not found: {file_path}", err=True)
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()

    try:
        report = None
        if ext in [".xlsx", ".xls"]:
            click.echo(f"Loading Excel file: {file_path}...")
            report = ProfileReport.from_excel(file_path, title=title, minimal=minimal)
        elif ext == ".parquet":
            click.echo(f"Loading Parquet file: {file_path}...")
            table = ibis.read_parquet(file_path)
            report = ProfileReport(table, minimal=minimal, title=title)
        elif ext == ".csv":
            click.echo(f"Loading CSV file: {file_path}...")
            table = ibis.read_csv(file_path)
            report = ProfileReport(table, minimal=minimal, title=title)
        else:
            # Fallback/Attempt to load as Parquet or CSV
            try:
                click.echo(f"Attempting to load {file_path} as Parquet...")
                table = ibis.read_parquet(file_path)
            except Exception:
                click.echo(f"Attempting to load {file_path} as CSV...")
                table = ibis.read_csv(file_path)
            report = ProfileReport(table, minimal=minimal, title=title)

        if not output_format:
            output_format = "json" if output.endswith(".json") else "html"

        click.echo(f"Generating {output_format.upper()} report...")
        if output_format == "json":
            # Ensure output ends in .json if forced but filename doesn't
            if not output.endswith(".json") and output_format == "json":
                output += ".json"
            report.to_file(output)
        else:
            report.to_file(output, theme=theme)

        click.echo(f"Report successfully generated: {output}")

    except Exception as e:
        click.echo(f"Error during profiling: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
