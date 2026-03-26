import pandas as pd
import numpy as np


def generate_static_benchmark_data(
    n_cols=100, n_rows=10000, output_path="/tmp/ibis-profiling/bench_reclass_static.parquet"
):
    print(f"Generating {n_cols}x{n_rows} dataset...")
    # Seed for reproducibility
    np.random.seed(42)
    data = {f"col_{i}": np.random.randint(0, 2, n_rows) for i in range(n_cols)}
    df = pd.DataFrame(data)
    df.to_parquet(output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    generate_static_benchmark_data()
