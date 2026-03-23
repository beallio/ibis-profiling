import os
import time
import tracemalloc
import gc
import json
import polars as pl
import numpy as np

# Ensure we use the local src
import sys

sys.path.insert(0, os.getcwd() + "/src")

from ibis_profiling import ProfileReport

DATA_PATH = "/tmp/ibis-profiling/benchmark_excel.xlsx"
ROWS = 100_000
COLS = 20


def generate_data():
    if os.path.exists(DATA_PATH):
        print(f"Data already exists at {DATA_PATH}. Skipping generation.")
        return

    print(f"Generating test Excel file: {ROWS} rows x {COLS} cols...")
    data = {f"col_{i}": np.random.randn(ROWS) for i in range(COLS)}
    df = pl.DataFrame(data)
    df.write_excel(DATA_PATH)
    print("Done generating.")


def run_benchmark():
    gc.collect()
    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        # We pass profiling kwargs and read_excel kwargs to test the routing
        report = ProfileReport.from_excel(
            DATA_PATH,
            minimal=True,
            correlations=False,
            compute_duplicates=False,
            title="Benchmark Excel",
            engine_options={},  # Test polars kwarg pass-through
        )
        _ = report.to_json()  # Trigger computation
        duration = time.perf_counter() - start_time
        _, peak_memory = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    print(json.dumps({"duration": duration, "peak_memory": peak_memory}, indent=2))


if __name__ == "__main__":
    generate_data()
    print("Running benchmark...")
    run_benchmark()
