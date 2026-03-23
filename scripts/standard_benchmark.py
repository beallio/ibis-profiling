import ibis
import pandas as pd
import numpy as np
import time
import tracemalloc
import os
import json
from ibis_profiling import ProfileReport


def run_benchmark():
    n = 1_000_000
    print("Standard Benchmark: 1M rows, 10 columns")

    # Generate deterministic data for comparison
    np.random.seed(42)
    data = {
        "id": np.arange(n),
        "val1": np.random.randn(n),
        "val2": np.random.randn(n),
        "cat1": np.random.choice(["A", "B", "C", "D"], n),
        "cat2": np.random.choice(["X", "Y"], n),
        "ints": np.random.randint(0, 100, n),
        "nulls": np.random.choice([np.nan, 1.0], n),
        "skewed": np.random.pareto(2, n),
        "const": np.ones(n),
        "unique_str": [f"S_{i}" for i in range(n)],
    }

    df = pd.DataFrame(data)
    con = ibis.duckdb.connect()
    table = con.create_table("bench", df)

    results = {}

    for mode in ["minimal", "full"]:
        print(f"  Running {mode} mode...")
        gc_collect()
        tracemalloc.start()
        start_time = time.perf_counter()

        report = ProfileReport(table, minimal=(mode == "minimal"))
        _ = report.to_json()

        duration = time.perf_counter() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        results[mode] = {"duration": duration, "peak_mb": peak / (1024 * 1024)}
        print(f"    {duration:.2f}s, {results[mode]['peak_mb']:.2f}MB")

    return results


def gc_collect():
    import gc

    gc.collect()


if __name__ == "__main__":
    res = run_benchmark()
    output_dir = "/tmp/ibis-profiling"
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/standard_bench_results.json", "w") as f:
        json.dump(res, f, indent=2)
