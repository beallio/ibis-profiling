import ibis
import polars as pl
import time
import os
from ibis_profiling.logical_types import IbisLogicalTypeSystem


def generate_bench_data(n_rows, path):
    print(f"Generating {n_rows:,} rows...")
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
        }
    )
    df.write_parquet(path)
    return ibis.read_parquet(path)


def bench():
    path_1m = "/tmp/ibis-profiling/bench_1m.parquet"
    path_10m = "/tmp/ibis-profiling/bench_10m.parquet"

    os.makedirs("/tmp/ibis-profiling", exist_ok=True)

    t1 = generate_bench_data(1_000_000, path_1m)
    t2 = generate_bench_data(10_000_000, path_10m)

    ts = IbisLogicalTypeSystem()

    # Warmup
    ts.infer_all_types(t1)

    print("\n--- Benchmarking Logical Inference (with 10k sampling) ---")

    start = time.perf_counter()
    ts.infer_all_types(t1)
    duration_1m = time.perf_counter() - start
    print(f"1M rows inference time: {duration_1m:.4f}s")

    start = time.perf_counter()
    ts.infer_all_types(t2)
    duration_10m = time.perf_counter() - start
    print(f"10M rows inference time: {duration_10m:.4f}s")

    delta = abs(duration_10m - duration_1m)
    print(f"\nDelta: {delta:.4f}s")
    if delta < 0.1:
        print("VERIFIED: Inference time is near-constant (Sampling is effective).")
    else:
        print("FAILED: Inference time scales with data size.")


if __name__ == "__main__":
    bench()
