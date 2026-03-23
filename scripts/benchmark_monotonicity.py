import ibis
import pandas as pd
import numpy as np
import time
import os
from ibis_profiling import profile


def generate_data(n=1_000_000):
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
    table = generate_data(1_000_000)

    print("\n--- Benchmarking Monotonicity ---")

    # 1. With Monotonicity (Forced)
    print("Running with Monotonicity ENABLED (forced)...")
    start = time.time()
    profile(table, monotonicity=True)
    duration_enabled = time.time() - start
    print(f"Duration (Enabled): {duration_enabled:.2f}s")

    # 2. Without Monotonicity (Skipped via threshold)
    print("\nRunning with Monotonicity SKIPPED (threshold=100k)...")
    start = time.time()
    profile(table, monotonicity_threshold=100_000)
    duration_skipped = time.time() - start
    print(f"Duration (Skipped): {duration_skipped:.2f}s")

    improvement = (duration_enabled - duration_skipped) / duration_enabled * 100
    print(f"\nPerformance Improvement: {improvement:.2f}%")

    # Save results to /tmp
    results_path = "/tmp/ibis-profiling/monotonicity_benchmark.txt"
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "w") as f:
        f.write("Monotonicity Benchmark Results (1M rows)\n")
        f.write(f"Enabled: {duration_enabled:.2f}s\n")
        f.write(f"Skipped: {duration_skipped:.2f}s\n")
        f.write(f"Improvement: {improvement:.2f}%\n")
    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
