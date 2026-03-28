import pandas as pd
import numpy as np


def generate_varied_data(n_rows, output_path):
    print(f"Generating {n_rows} rows of varied data...")
    # Seed for reproducibility
    np.random.seed(42)

    data = {
        "id": np.arange(n_rows),  # Unique (Optimization candidate)
        "cat_low": np.random.choice(["A", "B", "C", "D", "E"], n_rows),  # Low cardinality
        "cat_high": np.random.randint(0, n_rows // 2, n_rows).astype(
            str
        ),  # High cardinality (Skip candidate)
        "num_cont": np.random.randn(n_rows),  # Continuous
        "num_disc": np.random.randint(0, 100, n_rows),  # Discrete
        "bool_col": np.random.choice([True, False], n_rows),
        "mostly_null": [1 if i % 10 == 0 else None for i in range(n_rows)],
        "num_high_card": np.random.randint(
            0, n_rows - 100, n_rows
        ),  # High cardinality int (Skip candidate)
        "date_col": pd.date_range("2020-01-01", periods=1000).repeat(n_rows // 1000 + 1)[:n_rows],
        "const_col": [42] * n_rows,
    }

    df = pd.DataFrame(data)
    df.to_parquet(output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    import sys

    rows = int(sys.argv[1]) if len(sys.argv) > 1 else 5_000_000
    path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/ibis-profiling/varied_data.parquet"
    generate_varied_data(rows, path)
