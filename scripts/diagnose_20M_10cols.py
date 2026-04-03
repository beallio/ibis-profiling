# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "polars",
#   "pyarrow",
#   "numpy",
#   "psutil",
# ]
# ///
import ibis
import time
import os
import polars as pl
import numpy as np
import psutil
import gc
from ibis_profiling import ProfileReport


def get_mem_mb():
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0


def generate_data_20M_10cols(n_rows):
    """Generates 20M rows x 10 columns of data."""
    rng = np.random.default_rng(42)
    print(f"[{get_mem_mb():.2f} MB] Generating data dictionary...")

    # Exactly 10 columns
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

    print(f"[{get_mem_mb():.2f} MB] Creating Polars DataFrame...")
    df = pl.DataFrame(data)
    del data
    gc.collect()

    return df


def main():
    n_rows = 20_000_000
    temp_dir = "/tmp/ibis-profiling"
    data_path = f"{temp_dir}/data_20M_empty_10cols.parquet"
    report_path = f"{temp_dir}/report_20M_empty_10cols.html"

    os.makedirs(temp_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print(f"Generating {n_rows:,} rows x 10 columns...")
        start_gen = time.time()
        df = generate_data_20M_10cols(n_rows)
        df.write_parquet(data_path)
        print(f"Data generation and save took {time.time() - start_gen:.2f}s")
        del df
        gc.collect()
    else:
        print(f"Using existing data at {data_path}")

    print(f"\n[{get_mem_mb():.2f} MB] Connecting to data with Ibis...")
    con = ibis.duckdb.connect()
    # Explicitly set DuckDB memory limit if needed (optional)
    # con.execute("SET memory_limit='2GB'")
    table = con.read_parquet(data_path)

    start_prof = time.time()

    def on_progress(inc, label):
        if label:
            print(f"[{time.time() - start_prof:.2f}s][{get_mem_mb():.2f} MB] {label}")

    print("--- Profiling 20M rows x 10 columns (FULL) ---")
    try:
        # Full profiling (minimal=False, parallel=False for isolation)
        report = ProfileReport(
            table,
            minimal=False,
            parallel=False,
            on_progress=on_progress,
            title="20M Rows x 10 Columns (Empty String Col) Report",
        )
        duration_prof = time.time() - start_prof
        print(f"Profiling took: {duration_prof:.2f}s")

        print(f"Saving report to {report_path}...")
        report.to_file(report_path, minify=True)
        print("Report saved successfully.")
    except Exception as e:
        print(f"Profiling FAILED: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
