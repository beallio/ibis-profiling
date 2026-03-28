import ibis
import time
from ibis_profiling import Profiler


def run_benchmark(path="/tmp/ibis-profiling/bench_varied_20M.parquet"):
    print(f"Loading data from {path}...")
    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    # Standard settings for this bottleneck test
    profiler = Profiler(
        table, correlations=False, monotonicity=False, compute_duplicates=False, minimal=False
    )

    print("Starting profiling...")
    start_time = time.time()
    report = profiler.run()
    end_time = time.time()

    duration = end_time - start_time
    print(f"Profiling took: {duration:.2f} seconds")

    # Check a few keys to verify logic
    # id is unique (literal optimization)
    # cat_high is skip candidate
    for col in ["id", "cat_high"]:
        n_unique = report.variables[col].get("n_unique")
        print(f"  {col} n_unique: {n_unique}")

    return duration


if __name__ == "__main__":
    run_benchmark()
