import json

import ibis
import polars as pl

from tools.benchmark import benchmark_profile
from tools.datasets import generate_dataframe, write_parquet
from tools.reports import render_report


def test_generate_dataframe_is_seeded_and_has_requested_shape(tmp_path):
    frame = generate_dataframe(rows=12, columns=6, seed=7)

    assert frame.shape == (12, 6)
    assert frame.equals(generate_dataframe(rows=12, columns=6, seed=7))
    assert {
        pl.Int64,
        pl.Float64,
        pl.String,
        pl.Datetime("us"),
    }.issubset(set(frame.dtypes))

    output = tmp_path / "synthetic.parquet"
    assert write_parquet(output, rows=12, columns=6, seed=7) == output
    assert pl.read_parquet(output).equals(frame)


def test_benchmark_profile_returns_timing_statistics():
    table = ibis.memtable(generate_dataframe(rows=20, columns=4))

    result = benchmark_profile(table, repeat=2, minimal=True)

    assert set(result) == {"min_seconds", "median_seconds", "mean_seconds", "max_seconds"}
    assert 0 <= result["min_seconds"] <= result["mean_seconds"] <= result["max_seconds"]
    assert result["min_seconds"] <= result["median_seconds"] <= result["max_seconds"]


def test_render_report_writes_json(tmp_path):
    table = ibis.memtable(generate_dataframe(rows=20, columns=4))
    output = tmp_path / "report.json"

    assert render_report(table, output, fmt="json", minimal=True) == output

    report = json.loads(output.read_text())
    assert report["table"]["n"] == 20
