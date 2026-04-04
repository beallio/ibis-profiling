import ibis
import polars as pl
from ibis_profiling.logical_types import JSON, IbisLogicalTypeSystem


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
