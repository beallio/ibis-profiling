import ibis
import pandas as pd
import numpy as np
import time
import os
import argparse
from ibis_profiling import profile


def generate_data(n=5_000_000):
    print(f"Generating {n:,} rows of data...")
    rng = np.random.default_rng(42)
    data = {
        "id": np.arange(n),
        "val1": rng.normal(100, 15, n),
        "val2": np.sort(rng.uniform(0, 1000, n)),
        "val3": rng.uniform(0, 1000, n),
    }
    return ibis.memtable(pd.DataFrame(data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5_000_000)
    parser.add_argument("--iterations", type=int, default=10)
    args = parser.parse_args()

    n_rows = args.rows
    n_iters = args.iterations

    table = generate_data(n_rows)

    print(f"\n--- Benchmarking Monotonicity ({n_rows:,} rows, {n_iters} iterations) ---")

    enabled_times = []
    skipped_times = []

    for i in range(n_iters):
        print(f"Iteration {i + 1}/{n_iters}...")

        # 1. With Monotonicity (Forced)
        start = time.time()
        profile(table, monotonicity=True, cardinality_threshold=0)
        enabled_times.append(time.time() - start)

        # 2. Without Monotonicity (Skipped via threshold)
        start = time.time()
        profile(table, monotonicity_threshold=100_000, cardinality_threshold=0)
        skipped_times.append(time.time() - start)

    avg_enabled = sum(enabled_times) / n_iters
    avg_skipped = sum(skipped_times) / n_iters

    improvement = (avg_enabled - avg_skipped) / avg_enabled * 100

    print("\nResults:")
    print(f"Average Duration (Enabled): {avg_enabled:.2f}s")
    print(f"Average Duration (Skipped): {avg_skipped:.2f}s")
    print(f"Average Improvement: {improvement:.2f}%")

    # Save results to /tmp
    results_path = "/tmp/ibis-profiling/monotonicity_benchmark_5M.txt"
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "w") as f:
        f.write(f"Monotonicity Benchmark Results ({n_rows:,} rows, {n_iters} iters)\n")
        f.write(f"Average Enabled: {avg_enabled:.2f}s\n")
        f.write(f"Average Skipped: {avg_skipped:.2f}s\n")
        f.write(f"Improvement: {improvement:.2f}%\n")
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
