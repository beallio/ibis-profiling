# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "polars",
#   "pyarrow",
#   "numpy",
# ]
# ///
import ibis
import time
import os
import polars as pl
import numpy as np
from ibis_profiling import ProfileReport

import gc


def generate_data_10M_20cols(n_rows):
    """Generates 10M rows x 20 columns of data with one empty string column."""
    rng = np.random.default_rng(42)

    # Generate columns with pure numpy/primitive types
    data = {
        "id": np.arange(n_rows, dtype=np.int64),
        "int_col": rng.integers(0, 1000, size=n_rows, dtype=np.int32),
        "float_col": rng.uniform(0, 1, size=n_rows).astype(np.float32),
        "bool_col": rng.choice([True, False], size=n_rows),
        "cat_low": rng.choice(["A", "B", "C"], size=n_rows),
        "cat_high": rng.integers(0, 10000, size=n_rows, dtype=np.int32).astype(str),
        "date_col": np.arange(1600000000, 1600000000 + n_rows, dtype=np.int64),
        "const_int": np.full(n_rows, 42, dtype=np.int32),
        "random_str": rng.choice(["foo", "bar", "baz", "qux"], size=n_rows),
        "empty_strings": np.full(n_rows, "", dtype=str),
    }

    # Add 10 more columns to reach 20 total
    for i in range(10):
        data[f"extra_col_{i}"] = rng.uniform(0, 100, size=n_rows).astype(np.float32)

    df = pl.DataFrame(data)
    del data
    gc.collect()

    # Inject nulls for "mostly_null" using Polars
    df = df.with_columns(
        [
            pl.when(pl.Series(rng.random(n_rows) > 0.9))
            .then(pl.lit(rng.integers(0, 100, n_rows, dtype=np.int32)))
            .otherwise(None)
            .alias("mostly_null")
        ]
    )

    gc.collect()

    return df


def main():
    n_rows = 10_000_000
    temp_dir = "/tmp/ibis-profiling"
    data_path = f"{temp_dir}/data_10M_empty.parquet"
    report_path = f"{temp_dir}/report_10M_empty.html"

    os.makedirs(temp_dir, exist_ok=True)

    print(f"Generating {n_rows:,} rows x 20 columns of data...")
    start_gen = time.time()
    df = generate_data_10M_20cols(n_rows)
    df.write_parquet(data_path)
    print(f"Data generation and save took {time.time() - start_gen:.2f}s")

    print("\n--- Profiling 10M rows dataset ---")
    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    start_prof = time.time()

    def on_progress(inc, label):
        if label:
            print(f"[{time.time() - start_prof:.2f}s] {label}")

    # Using minimal=False and parallel=False to try full profiling
    report = ProfileReport(
        table,
        minimal=False,
        parallel=False,
        on_progress=on_progress,
        title="10M Rows x 20 Columns (Empty String Col) Report",
    )
    duration_prof = time.time() - start_prof
    print(f"Profiling took: {duration_prof:.2f}s")

    print(f"Saving report to {report_path}...")
    report.to_file(report_path, minify=True)

    json_path = report_path.replace(".html", ".json")
    print(f"Saving JSON to {json_path}...")
    report.to_file(json_path)
    print("Report saved successfully.")


if __name__ == "__main__":
    main()
