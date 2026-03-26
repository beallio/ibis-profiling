import ibis
import pandas as pd
import numpy as np
import time
from unittest.mock import patch, MagicMock
from ibis_profiling import Profiler


def benchmark_parallel(backend_name="pandas", parallel=True, n_cols=50, n_rows=10000):
    # Create static data
    np.random.seed(42)
    data = {f"col_{i}": np.random.randn(n_rows) for i in range(n_cols)}
    df = pd.DataFrame(data)

    # Use memtable (usually duckdb) but we will mock the backend name
    table = ibis.memtable(df)

    print(f"Benchmarking with mock {backend_name} (parallel={parallel})...")

    # Mock the backend name to test the allowlist path
    with patch("ibis.expr.types.relations.Table.get_backend") as mock_get_backend:
        mock_con = MagicMock()
        mock_con.name = backend_name
        mock_get_backend.return_value = mock_con

        durations = []
        for i in range(10):
            profiler = Profiler(table, parallel=parallel, pool_size=4, minimal=False)
            start = time.perf_counter()
            profiler.run()
            end = time.perf_counter()
            durations.append(end - start)
            print(f"Iteration {i + 1}: {end - start:.4f}s")

        avg = sum(durations) / len(durations)
        print(f"\nAverage Duration: {avg:.4f}s")
        return avg


if __name__ == "__main__":
    import sys

    # Default to 'pandas' (allowlisted) to verify no overhead in safe path
    # Use '--unsafe' to test the sequential fallback impact
    backend = "postgres" if "--unsafe" in sys.argv else "pandas"
    p = "--parallel" in sys.argv
    benchmark_parallel(backend_name=backend, parallel=p)
