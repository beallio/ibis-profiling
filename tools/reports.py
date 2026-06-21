"""Render HTML or JSON profiling reports from an Ibis table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Literal

import ibis

from ibis_profiling import profile

ReportFormat = Literal["html", "json"]


def render_report(
    table: ibis.Table,
    out_path: str | Path,
    *,
    fmt: ReportFormat = "html",
    **profile_kwargs: Any,
) -> Path:
    """Profile a table and write an HTML or JSON report."""
    if fmt not in {"html", "json"}:
        raise ValueError("fmt must be 'html' or 'json'")

    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = profile(table, **profile_kwargs)
    if fmt == "html":
        output.write_text(report.to_html(), encoding="utf-8")
    else:
        output.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquet")
    parser.add_argument("out", type=Path)
    parser.add_argument("--format", choices=("html", "json"), default="html")
    parser.add_argument("--minimal", action="store_true")
    args = parser.parse_args()

    connection = ibis.duckdb.connect()
    table = connection.read_parquet(args.parquet)
    output = render_report(table, args.out, fmt=args.format, minimal=args.minimal)
    print(output)


if __name__ == "__main__":
    main()
