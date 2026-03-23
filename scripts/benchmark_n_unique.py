import ibis
import pandas as pd
import numpy as np
import time
from ibis_profiling import ProfileReport


def generate_benchmark_data(n_rows=100_000, n_cols=500):
    print(f"Generating {n_rows} rows x {n_cols} columns...")
    data = {}
    for i in range(n_cols):
        # Mix of unique, duplicates, and nulls
        col_name = f"col_{i}"
        if i % 3 == 0:
            # High cardinality (mostly unique)
            data[col_name] = np.arange(n_rows)
        elif i % 3 == 1:
            # Low cardinality (lots of duplicates)
            data[col_name] = np.random.randint(0, 100, size=n_rows)
        else:
            # Mix with nulls
            vals = np.random.randint(0, 1000, size=n_rows).astype(float)
            vals[np.random.choice(n_rows, n_rows // 10, replace=False)] = np.nan
            data[col_name] = vals

    return pd.DataFrame(data)


def run_benchmark(n_rows=10_000, n_cols=100):
    df = generate_benchmark_data(n_rows, n_cols)
    con = ibis.duckdb.connect()
    t = con.create_table("bench", df)

    # Custom progress to time steps
    def timed_progress(pct, msg):
        current_time = time.time()
        elapsed = current_time - timed_progress.last_time
        if timed_progress.last_msg:
            print(f"  Step '{timed_progress.last_msg}' took {elapsed:.2f}s")
        if msg:
            print(f"[{pct:>3}%] {msg}...")
        timed_progress.last_time = current_time
        timed_progress.last_msg = msg

    timed_progress.last_time = time.time()
    timed_progress.last_msg = None

    start_time = time.time()
    profile = ProfileReport(
        t,
        on_progress=timed_progress,
        minimal=False,
        correlations=False,
        compute_duplicates=False,
        monotonicity=False,
    )
    report = profile.to_json()
    end_time = time.time()

    duration = end_time - start_time
    print(f"Profile completed in {duration:.2f} seconds.")

    # Verify n_unique is present
    import json

    data = json.loads(report)
    n_unique_found = sum(1 for v in data["variables"].values() if "n_unique" in v)
    print(f"n_unique metrics found: {n_unique_found} / {n_cols}")


if __name__ == "__main__":
    import sys

    n_cols = 500
    n_rows = 100_000
    if len(sys.argv) > 1:
        n_cols = int(sys.argv[1])
    if len(sys.argv) > 2:
        n_rows = int(sys.argv[2])
    run_benchmark(n_cols=n_cols, n_rows=n_rows)
