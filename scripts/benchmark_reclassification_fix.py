import ibis
import pandas as pd
import time
import numpy as np
from ibis_profiling import Profiler


def benchmark_reclassification(n_cols=100, n_rows=1000):
    # Create a table with many low-cardinality integer columns
    data = {f"col_{i}": np.random.randint(0, 2, n_rows) for i in range(n_cols)}
    df = pd.DataFrame(data)
    table = ibis.memtable(df)

    durations = []
    for i in range(10):
        profiler = Profiler(
            table,
            cardinality_threshold=5,
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
