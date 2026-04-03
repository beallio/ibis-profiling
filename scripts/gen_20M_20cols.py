# /// script
# dependencies = [
#   "polars",
#   "numpy",
#   "psutil",
# ]
# ///
import os
import polars as pl
import numpy as np
import psutil
import gc


def get_mem_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def generate_data_20M_20cols(n_rows, output_path):
    rng = np.random.default_rng(42)
    print(f"[{get_mem_mb():.2f} MB] Starting 20-column generation...")

    # 20 columns
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

    # Add 10 more to reach 20
    for i in range(10):
        data[f"extra_{i}"] = rng.uniform(0, 100, size=n_rows).astype(np.float32)

    print(f"[{get_mem_mb():.2f} MB] Creating Polars DataFrame...")
    df = pl.DataFrame(data)
    del data
    gc.collect()

    print(f"[{get_mem_mb():.2f} MB] Writing to {output_path}...")
    df.write_parquet(output_path)
    print(f"[{get_mem_mb():.2f} MB] Done.")


if __name__ == "__main__":
    n_rows = 20_000_000
    path = "/tmp/ibis-profiling/data_20M_20cols.parquet"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    generate_data_20M_20cols(n_rows, path)
