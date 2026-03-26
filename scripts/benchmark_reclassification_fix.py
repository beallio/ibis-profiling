import ibis
import time
from ibis_profiling import Profiler


def benchmark_reclassification(input_path="/tmp/ibis-profiling/bench_reclass_static.parquet"):
    print(f"Loading dataset from {input_path}...")
    table = ibis.read_parquet(input_path)

    durations = []
    for i in range(10):
        # We must re-create the profiler each time to clear state
        profiler = Profiler(
            table,
            cardinality_threshold=20,
            correlations=False,
            monotonicity=False,
            compute_duplicates=False,
        )
        start = time.perf_counter()
        profiler.run()
        end = time.perf_counter()
        durations.append(end - start)
        print(f"Iteration {i + 1}: {end - start:.4f}s")

    avg = sum(durations) / len(durations)
    print(f"\nAverage Duration: {avg:.4f}s")
    return avg


if __name__ == "__main__":
    benchmark_reclassification()
