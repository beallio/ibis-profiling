import ibis
import polars as pl
from ibis_profiling.logical_types import JSON, CUID, NanoID, IbisLogicalTypeSystem


def test_json_detection():
    valid_json = [
        '{"a": 1, "b": [1, 2, 3]}',
        '[{"id": 1}, {"id": 2}]',
        '  {"key": "value"}  ',  # with whitespace
        "[]",
        "{}",
    ]

    invalid_json = ["just a string", "123", '{"missing_brace": 1', "not json at all"]

    ts = IbisLogicalTypeSystem()

    # Test valid
    df = pl.DataFrame({"j": valid_json})
    table = ibis.memtable(df)
    results = ts.infer_all_types(table)
    assert results["j"] == JSON

    # Test invalid
    df_invalid = pl.DataFrame({"j": invalid_json})
    table_invalid = ibis.memtable(df_invalid)
    results_invalid = ts.infer_all_types(table_invalid)
    assert results_invalid["j"] != JSON


def test_cuid_detection():
    valid_cuids = [
        "cjld2cyuq0000t3pz76272639",
        "cju0sr8lb0000p9884a4p6h9b",
    ]
    invalid_cuids = [
        "not-a-cuid",
        "cjld2cyuq0000t3pz7627263",  # Too short
        "bjld2cyuq0000t3pz76272639",  # Wrong start
    ]
    ts = IbisLogicalTypeSystem()

    # Test valid
    df = pl.DataFrame({"c": valid_cuids})
    table = ibis.memtable(df)
    results = ts.infer_all_types(table)
    assert results["c"] == CUID

    # Test invalid
    df_invalid = pl.DataFrame({"c": invalid_cuids})
    table_invalid = ibis.memtable(df_invalid)
    results_invalid = ts.infer_all_types(table_invalid)
    assert results_invalid["c"] != CUID


def test_nanoid_detection():
    valid_nanoids = [
        "V1StGXR8_Z5jdHi6B-myT",
        "78_Z5jdHi6B-myT-V1StG",
    ]
    invalid_nanoids = [
        "too-short",
        "this-is-too-long-for-a-nanoid-surely",
        "contains!invalid@char",
    ]
    ts = IbisLogicalTypeSystem()

    # Test valid
    df = pl.DataFrame({"n": valid_nanoids})
    table = ibis.memtable(df)
    results = ts.infer_all_types(table)
    assert results["n"] == NanoID

    # Test invalid
    df_invalid = pl.DataFrame({"n": invalid_nanoids})
    table_invalid = ibis.memtable(df_invalid)
    results_invalid = ts.infer_all_types(table_invalid)
    assert results_invalid["n"] != NanoID
