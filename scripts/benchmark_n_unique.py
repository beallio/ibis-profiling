import ibis
import pandas as pd
import numpy as np
import time
import os
from ibis_profiling import Profiler


def generate_data(n_rows=20_000_000, output_path="/tmp/ibis-profiling/bench_nunique.parquet"):
    if os.path.exists(output_path):
        print(f"File {output_path} already exists. Skipping generation.")
        return

    print(f"Generating {n_rows} rows of data...")
    # Create 3 columns:
    # 1. Low cardinality (10 values)
    # 2. Medium cardinality (1000 values)
    # 3. High cardinality (Unique values)

    df = pd.DataFrame(
        {
            "low_card": np.random.randint(0, 10, n_rows),
            "med_card": np.random.randint(0, 1000, n_rows),
            "high_card": np.arange(n_rows),
        }
    )

    df.to_parquet(output_path)
    print(f"Data saved to {output_path}")


def run_benchmark(n_rows=20_000_000):
    path = f"/tmp/ibis-profiling/bench_nunique_{n_rows}.parquet"
    generate_data(n_rows, path)

    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    print(f"\n--- Benchmarking {n_rows} rows ---")

    # 1. Without threshold (forced always on)
    print("\nRunning WITHOUT threshold (disabled via 0)...")
    profiler_off = Profiler(
        table,
        n_unique_threshold=0,
        correlations=False,
        monotonicity=False,
        compute_duplicates=False,
        minimal=False,
    )
    start_off = time.time()
    report_off = profiler_off.run()
    duration_off = time.time() - start_off
    print(f"Profiling (No Threshold) took: {duration_off:.2f} seconds")
    print(f"high_card n_unique: {report_off.variables['high_card'].get('n_unique')}")

    # 2. With threshold (default 1M)
    print("\nRunning WITH default threshold (1,000,000)...")
    profiler_on = Profiler(
        table, correlations=False, monotonicity=False, compute_duplicates=False, minimal=False
    )
    start_on = time.time()
    report_on = profiler_on.run()
    duration_on = time.time() - start_on
    print(f"Profiling (With Threshold) took: {duration_on:.2f} seconds")
    print(f"high_card n_unique: {report_on.variables['high_card'].get('n_unique')}")

    speedup = duration_off - duration_on
    print(f"\nSpeedup: {speedup:.2f} seconds ({(speedup / duration_off) * 100:.1f}%)")


if __name__ == "__main__":
    # Test with 20M rows
    run_benchmark(20_000_000)
