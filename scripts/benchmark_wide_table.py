import ibis
import numpy as np
import pandas as pd
import time
from ibis_profiling import ProfileReport


def run_benchmark(num_cols=500, num_rows=1000):
    print(f"Generating wide table with {num_cols} columns and {num_rows} rows...")
    df = pd.DataFrame({f"col_{i}": np.random.rand(num_rows) for i in range(num_cols)})
    con = ibis.duckdb.connect()
    table = con.create_table("wide_bench", df, temp=True)

    print("\nRunning Unbatched (batch_size=10000)...")
    start = time.perf_counter()
    ProfileReport(table, global_batch_size=10000).to_dict()
    unbatched_time = time.perf_counter() - start
    print(f"Unbatched time: {unbatched_time:.2f}s")

    print("\nRunning Batched (batch_size=500)...")
    start = time.perf_counter()
    ProfileReport(table, global_batch_size=500).to_dict()
    batched_time = time.perf_counter() - start
    print(f"Batched time: {batched_time:.2f}s")

    delta = ((batched_time - unbatched_time) / unbatched_time) * 100
    print(f"\nPerformance delta: {delta:.2f}%")


if __name__ == "__main__":
    run_benchmark()
