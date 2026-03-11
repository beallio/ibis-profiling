# /// script
# dependencies = [
#   "polars",
#   "numpy",
#   "pyarrow",
# ]
# ///
import polars as pl
import numpy as np
import argparse


def generate_alert_dataset(n_rows=100000):
    rng = np.random.default_rng(42)

    data = {
        "id": np.arange(n_rows),  # UNIQUE
        "constant_str": ["constant_value"] * n_rows,  # CONSTANT
        "mostly_missing": [None if i % 2 == 0 else 1.0 for i in range(n_rows)],  # MISSING (50%)
        "mostly_zeros": [0.0 if i % 10 != 0 else 1.0 for i in range(n_rows)],  # ZEROS (90%)
        "high_cardinality": [f"user_{i}" for i in range(n_rows)],  # HIGH_CARDINALITY (Categorical)
        "normal_numeric": rng.normal(100, 10, size=n_rows),
        "boolean_alert": [True] * n_rows,  # CONSTANT
    }

    return pl.DataFrame(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100000)
    parser.add_argument("--output", type=str, default="/tmp/ibis-profiling/alert_test_data.parquet")
    args = parser.parse_args()

    print(f"Generating alert test data with {args.rows} rows...")
    df = generate_alert_dataset(args.rows)
    df.write_parquet(args.output)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
