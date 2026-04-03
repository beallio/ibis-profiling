# /// script
# dependencies = [
#   "polars",
#   "numpy",
#   "pyarrow",
# ]
# ///
import os
import sys
import polars as pl
import numpy as np


def generate_varied_data(n_rows, n_cols, output_path):
    """Generates a dataset with a mix of types, nulls, and empty strings."""
    rng = np.random.default_rng(42)

    data = {}

    # 1. Mandatory columns
    data["id"] = np.arange(n_rows, dtype=np.int64)
    data["empty_strings"] = np.full(n_rows, "", dtype=str)

    # 2. Add varied types to fill up n_cols
    # Cycle through types: int, float, bool, string, date
    types = ["int", "float", "bool", "str", "date"]

    remaining_cols = n_cols - 2
    for i in range(remaining_cols):
        col_name = f"col_{i}_{types[i % len(types)]}"
        t = types[i % len(types)]

        if t == "int":
            data[col_name] = rng.integers(0, 1000, size=n_rows, dtype=np.int32)
        elif t == "float":
            data[col_name] = rng.uniform(0, 1, size=n_rows).astype(np.float32)
        elif t == "bool":
            data[col_name] = rng.choice([True, False], size=n_rows)
        elif t == "str":
            data[col_name] = rng.choice(["A", "B", "C", "D", "E"], size=n_rows)
        elif t == "date":
            # Start from a fixed timestamp
            data[col_name] = np.arange(1600000000, 1600000000 + n_rows, dtype=np.int64)

    df = pl.DataFrame(data)

    # 3. Inject nulls (5% rate for most columns)
    for col_name in df.columns:
        if col_name == "id":
            continue

        # Inject nulls using Polars
        null_mask = rng.random(n_rows) < 0.05
        df = df.with_columns(
            [pl.when(pl.Series(null_mask)).then(None).otherwise(pl.col(col_name)).alias(col_name)]
        )

    print(f"Writing {n_rows}x{n_cols} to {output_path}...")
    df.write_parquet(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_bench_data_varied.py <rows> <cols> <output_path>")
        sys.exit(1)

    rows = int(sys.argv[1])
    cols = int(sys.argv[2])
    path = sys.argv[3]

    os.makedirs(os.path.dirname(path), exist_ok=True)
    generate_varied_data(rows, cols, path)
