import ibis
import pandas as pd
import numpy as np
import time
import os
from ibis_profiling import Profiler


def generate_data(
    n_rows=50_000_000, output_path="/tmp/ibis-profiling/bench_nunique_50000000.parquet"
):
    if os.path.exists(output_path):
        print(f"File {output_path} already exists. Skipping generation.")
        return

    print(f"Generating {n_rows} rows of data...")
    df = pd.DataFrame(
        {
            "low_card": np.random.randint(0, 10, n_rows),
            "med_card": np.random.randint(0, 1000, n_rows),
            "high_card": np.arange(n_rows),
        }
    )

    df.to_parquet(output_path)
    print(f"Data saved to {output_path}")


def run_benchmark(n_rows=50_000_000):
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
    profiler_off.run()
    duration_off = time.time() - start_off
    print(f"Profiling (No Threshold) took: {duration_off:.2f} seconds")

    # 2. With threshold (default 1M)
    print("\nRunning WITH default threshold (1,000,000)...")
    profiler_on = Profiler(
        table, correlations=False, monotonicity=False, compute_duplicates=False, minimal=False
    )
    start_on = time.time()
    profiler_on.run()
    duration_on = time.time() - start_on
    print(f"Profiling (With Threshold) took: {duration_on:.2f} seconds")

    speedup = duration_off - duration_on
    print(f"\nSpeedup: {speedup:.2f} seconds ({(speedup / duration_off) * 100:.1f}%)")


if __name__ == "__main__":
    run_benchmark(50_000_000)
