import ibis
import polars as pl
import time
import os
import logging
from ibis_profiling.logical_types import IbisLogicalTypeSystem

# Suppress logging for cleaner benchmark output
logging.getLogger().setLevel(logging.ERROR)


def generate_scale_data(n_rows, path):
    if os.path.exists(path):
        print(f"Using existing data at {path}")
        return ibis.read_parquet(path)

    print(f"Generating {n_rows:,} rows for scale testing...")
    df = pl.DataFrame(
        {
            "email": ["user@example.com"] * n_rows,
            "url": ["https://google.com"] * n_rows,
            "ip": ["192.168.1.1"] * n_rows,
            "cc": ["4111111111111111"] * n_rows,
            "ssn": ["123-45-6789"] * n_rows,
            "json": ['{"a": 1}'] * n_rows,
            "path": ["/var/log/syslog"] * n_rows,
            "geo": ["POINT(0 0)"] * n_rows,
            "currency": ["$100.00"] * n_rows,
            "string": ["just a normal string"] * n_rows,
            "integer": [123] * n_rows,
            "decimal": [1.23] * n_rows,
        }
    )
    df.write_parquet(path)
    return ibis.read_parquet(path)


def run_scale_test():
    n_rows = 10_000_000
    path = "/tmp/ibis-profiling/scale_10m_samples.parquet"
    os.makedirs("/tmp/ibis-profiling", exist_ok=True)

    table = generate_scale_data(n_rows, path)
    sample_sizes = [10_000, 100_000, 1_000_000, 5_000_000, None]

    print(f"\n--- Logical Inference Scale Test (Total Rows: {n_rows:,}) ---")
    print(f"{'Sample Size':<15} | {'Time (s)':<10} | {'Status'}")
    print("-" * 45)

    results = []
    for size in sample_sizes:
        label = f"{size:,}" if size is not None else "Full Scan"

        # Initialize system with specific sample size
        ts = IbisLogicalTypeSystem(inference_sample_size=size)

        # Warmup (optional, but good for stability)
        ts.infer_all_types(table)

        # Measure
        start = time.perf_counter()
        ts.infer_all_types(table)
        duration = time.perf_counter() - start

        print(f"{label:<15} | {duration:<10.4f}s | Success")
        results.append((label, duration))

    print("\n--- Summary ---")
    baseline = results[0][1]  # 10k
    for label, duration in results:
        multiplier = duration / baseline
        print(f"{label:<15}: {duration:.4f}s ({multiplier:.2f}x vs 10k)")


if __name__ == "__main__":
    run_scale_test()
