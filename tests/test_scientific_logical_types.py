import ibis
import polars as pl
from ibis_profiling.logical_types import Complex, Geometry, Currency, IbisLogicalTypeSystem


def test_complex_detection():
    valid = ["1+2j", "-3.14j", "0.5-0.5j", "10j"]
    invalid = ["1+2i", "abc", "1.2.3j"]

    ts = IbisLogicalTypeSystem()
    df = pl.DataFrame({"c": valid})
    assert ts.infer_all_types(ibis.memtable(df))["c"] == Complex

    df_inv = pl.DataFrame({"c": invalid})
    assert ts.infer_all_types(ibis.memtable(df_inv))["c"] != Complex


def test_geometry_detection():
    valid = [
        "POINT (30 10)",
        "LINESTRING (30 10, 10 30, 40 40)",
        "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))",
    ]
    invalid = ["POINT 30 10", "CIRCLE (10 10, 5)", "not wkt"]

    ts = IbisLogicalTypeSystem()
    df = pl.DataFrame({"g": valid})
    # Case-insensitive check
    assert ts.infer_all_types(ibis.memtable(df))["g"] == Geometry

    df_inv = pl.DataFrame({"g": invalid})
    assert ts.infer_all_types(ibis.memtable(df_inv))["g"] != Geometry


def test_currency_detection():
    valid = ["$100.00", "€50,000", "£10.50", "¥1000"]
    invalid = ["100.00", "US$100", "price: $10"]

    ts = IbisLogicalTypeSystem()
    df = pl.DataFrame({"c": valid})
    assert ts.infer_all_types(ibis.memtable(df))["c"] == Currency

    df_inv = pl.DataFrame({"c": invalid})
    assert ts.infer_all_types(ibis.memtable(df_inv))["c"] != Currency
