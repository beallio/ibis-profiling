import ibis
import time
import os
from ibis_profiling import Profiler


def run_bench(threshold=None, iterations=5):
    path = "/tmp/ibis-profiling/bench_varied_50M.parquet"
    if not os.path.exists(path):
        print(f"Error: Data not found at {path}")
        return 0

    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    durations = []
    for i in range(iterations):
        kwargs = {
            "correlations": False,
            "monotonicity": False,
            "compute_duplicates": False,
            "minimal": False,
        }
        if threshold is not None:
            kwargs["n_unique_threshold"] = threshold

        profiler = Profiler(table, **kwargs)

        start = time.perf_counter()
        profiler.run()
        end = time.perf_counter()
        durations.append(end - start)
        print(f"  Iteration {i + 1}: {end - start:.2f}s")

    avg = sum(durations) / len(durations)
    return avg


if __name__ == "__main__":
    import sys

    # Extract threshold from args if provided
    thresh = None
    if len(sys.argv) > 1 and sys.argv[1] != "None":
        thresh = int(sys.argv[1])

    avg_time = run_bench(threshold=thresh)
    print(f"AVERAGE: {avg_time:.2f}s")
