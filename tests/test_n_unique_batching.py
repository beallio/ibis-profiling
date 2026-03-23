import ibis
import pandas as pd
from ibis_profiling import profile


def test_n_unique_correctness():
    # Test dataset with various singleton patterns
    df = pd.DataFrame(
        {
            "all_unique": [1, 2, 3, 4, 5],
            "all_duplicates": [1, 1, 1, 1, 1],
            "mixed": [1, 2, 2, 3, 3],  # 1 is singleton
            "with_nulls": [1, 2, None, 1, None],  # 2 is singleton
            "all_nulls": pd.Series(
                [None, None, None, None, None], dtype="float64"
            ),  # Avoid NULL type
            "single_row": [42] + [None] * 4,  # 42 is singleton
        }
    )

    con = ibis.duckdb.connect()
    t = con.create_table("test_unique", df)

    # Run profile (minimal=False to ensure singleton pass runs)
    report = profile(
        t, minimal=False, correlations=False, compute_duplicates=False, monotonicity=False
    )

    vars = report.variables
    assert vars["all_unique"]["n_unique"] == 5
    assert vars["all_duplicates"]["n_unique"] == 0
    assert vars["mixed"]["n_unique"] == 1
    assert vars["with_nulls"]["n_unique"] == 1
    assert vars["all_nulls"]["n_unique"] == 0
    assert vars["single_row"]["n_unique"] == 1


def test_n_unique_single_row():
    df = pd.DataFrame({"a": [1]})
    con = ibis.duckdb.connect()
    t = con.create_table("test_single", df)
    report = profile(
        t, minimal=False, correlations=False, compute_duplicates=False, monotonicity=False
    )
    assert report.variables["a"]["n_unique"] == 1


def test_n_unique_empty():
    schema = ibis.schema({"a": "int64"})
    con = ibis.duckdb.connect()
    t = con.create_table("test_empty", schema=schema)
    report = profile(
        t, minimal=False, correlations=False, compute_duplicates=False, monotonicity=False
    )
    # n_unique should be 0 or handled gracefully
    assert report.variables["a"]["n_unique"] == 0
