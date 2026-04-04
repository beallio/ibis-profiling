import ibis
import polars as pl
from ibis_profiling.logical_types import MACAddress, CountryCode, FilePath, IbisLogicalTypeSystem


def test_mac_address_detection():
    valid = ["00:1A:2B:3C:4D:5E", "00-1a-2b-3c-4d-5e"]
    invalid = ["00:1A:2B:3C:4D", "G0:1A:2B:3C:4D:5E", "not-a-mac"]

    ts = IbisLogicalTypeSystem()
    df = pl.DataFrame({"m": valid})
    assert ts.infer_all_types(ibis.memtable(df))["m"] == MACAddress

    df_inv = pl.DataFrame({"m": invalid})
    assert ts.infer_all_types(ibis.memtable(df_inv))["m"] != MACAddress


def test_country_code_detection():
    valid = ["US", "USA", "GB", "GBR", "FR", "FRA"]
    invalid = ["U", "US1", "united states", "123"]

    ts = IbisLogicalTypeSystem()
    df = pl.DataFrame({"c": valid})
    assert ts.infer_all_types(ibis.memtable(df))["c"] == CountryCode

    df_inv = pl.DataFrame({"c": invalid})
    assert ts.infer_all_types(ibis.memtable(df_inv))["c"] != CountryCode


def test_file_path_detection():
    valid = [
        "/var/log/syslog",
        "C:\\Windows\\System32",
        "s3://my-bucket/data.csv",
        "gs://bucket/path",
    ]
    invalid = ["var/log", "just a file name.txt", "http://google.com"]

    ts = IbisLogicalTypeSystem()
    df = pl.DataFrame({"p": valid})
    assert ts.infer_all_types(ibis.memtable(df))["p"] == FilePath

    df_inv = pl.DataFrame({"p": invalid})
    assert ts.infer_all_types(ibis.memtable(df_inv))["p"] != FilePath
