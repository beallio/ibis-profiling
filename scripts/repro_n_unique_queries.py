import ibis
import time
from ibis_profiling import Profiler


def run_benchmark(path="/tmp/ibis-profiling/bench_varied_20M.parquet"):
    print(f"Loading data from {path}...")
    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    profiler = Profiler(
        table, correlations=False, monotonicity=False, compute_duplicates=False, minimal=False
    )

    print("Starting profiling...")
    start_time = time.time()
    profiler.run()
    end_time = time.time()

    duration = end_time - start_time
    print(f"Profiling took: {duration:.2f} seconds")
    return duration


if __name__ == "__main__":
    run_benchmark()
