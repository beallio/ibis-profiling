import ibis
import polars as pl
import time
import os
import logging

# Suppress logging for cleaner benchmark output
logging.getLogger().setLevel(logging.ERROR)


def generate_varied_data(n_rows, path):
    if os.path.exists(path):
        print(f"Loading existing benchmark data from {path}...")
        return ibis.read_parquet(path)

    print(f"Generating {n_rows:,} rows of SHUFFLED high-cardinality varied data...")

    # Define base values
    emails = ["user@example.com", "test.name@domain.co.uk", "admin@company.net"]
    urls = ["https://google.com", "http://domain.org/path", "ftp://files.com"]
    ips = ["192.168.1.1", "8.8.8.8", "127.0.0.1"]
    ccs = ["4111111111111111", "5105105105105105", "341234567890123"]
    ssns = ["123-45-6789", "999-00-1111", "555-55-5555"]
    jsons = ['{"id": 1}', '{"data": [1,2,3]}', '{"meta": {"ok": true}}']
    paths = ["/var/log/syslog", "C:\\Windows\\System32", "s3://bucket/data"]
    geos = ["POINT(0 0)", "LINESTRING(0 0, 1 1)", "POLYGON((0 0, 1 1, 1 0, 0 0))"]
    currencies = ["$10.00", "€50.00", "£100.00"]
    states = ["CA", "NY", "TX", "FL", "DC"]
    ibans = ["GB29NWBK60161331926819", "DE89370400440532013000"]
    uuids = ["550e8400-e29b-41d4-a716-446655440000", "123e4567-e89b-12d3-a456-426614174000"]

    # Create a small base dataframe
    base_df = pl.DataFrame(
        {
            "email": emails * 10,
            "url": urls * 10,
            "ip": ips * 10,
            "cc": ccs * 10,
            "ssn": ssns * 10,
            "json": jsons * 10,
            "path": paths * 10,
            "geo": geos * 10,
            "currency": currencies * 10,
            "state": (states * 6),
            "iban": (ibans * 15),
            "uuid": (uuids * 15),
        }
    )

    # Repeat to reach target rows
    repeats = (n_rows // base_df.height) + 1
    df = pl.concat([base_df] * repeats).head(n_rows)

    df = df.with_columns(cat_high=pl.Series([f"ID_{i}" for i in range(n_rows)]))
    df = df.with_columns(
        age=pl.Series([20 + (i % 60) for i in range(n_rows)]),
        zip=pl.Series([f"{10000 + (i % 80000)}" for i in range(n_rows)]),
    )

    df = df.sample(fraction=1.0, shuffle=True, seed=42)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.write_parquet(path)
    return ibis.read_parquet(path)


def run_bench():
    n_rows = 10_000_000
    path = f"/tmp/ibis-profiling/bench_varied_shuffled_{n_rows}.parquet"

    table = generate_varied_data(n_rows, path)

    from ibis_profiling.profiler import Profiler

    # Handle different Profiler init signatures across branches
    try:
        profiler = Profiler(table)
    except TypeError:
        profiler = Profiler()

    try:
        import subprocess

        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.STDOUT
            )
            .decode()
            .strip()
        )
    except Exception:
        branch = "Unknown"

    print(f"\n--- Benchmark: Branch '{branch}' ---")
    print(f"Dataset: {n_rows:,} rows, {len(table.columns)} columns")

    # Use _get_logical_types if available (new branch), otherwise fallback to empty dict
    def get_ltypes(t):
        if hasattr(profiler, "_get_logical_types"):
            return profiler._get_logical_types(t)
        return {}

    # Warmup
    get_ltypes(table)

    # 5 iterations
    iterations = 5
    durations = []

    for i in range(iterations):
        start = time.perf_counter()
        results = get_ltypes(table)
        durations.append(time.perf_counter() - start)
        print(f"Iteration {i + 1}: {durations[-1]:.4f}s")

    avg = sum(durations) / len(durations)
    print(f"\nAverage Inference Time: {avg:.4f}s")

    # Sanity check
    if results:
        print("\nDetected Types (Sample):")
        for col in sorted(results.keys())[:10]:
            name = getattr(results[col], "__name__", str(results[col]))
            print(f"  {col:<10}: {name}")
    else:
        print("\nNo logical types detected (Expected on 'dev' branch)")


if __name__ == "__main__":
    run_bench()
