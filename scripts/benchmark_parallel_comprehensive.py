import ibis
import pandas as pd
import numpy as np
import time
from unittest.mock import patch, MagicMock
from ibis_profiling import Profiler


def run_benchmark(backend_name, parallel=True, n_cols=5, n_rows=1000):
    np.random.seed(42)
    data = {f"col_{i}": np.random.randn(n_rows) for i in range(n_cols)}
    df = pd.DataFrame(data)
    table = ibis.memtable(df)

    print(f"START: Backend={backend_name}, Parallel={parallel}")

    with patch("ibis.expr.types.relations.Table.get_backend") as mock_get_backend:
        mock_con = MagicMock()
        mock_con.name = backend_name
        mock_get_backend.return_value = mock_con

        durations = []
        for i in range(5):
            profiler = Profiler(table, parallel=parallel, pool_size=4, minimal=True)
            start = time.perf_counter()
            profiler.run()
            end = time.perf_counter()
            durations.append(end - start)
            print(f"  Iter {i + 1}: {end - start:.4f}s")

        avg = sum(durations) / len(durations)
        print(f"FINISH: Avg={avg:.4f}s\n")
        return avg


if __name__ == "__main__":
    import sys

    backend = sys.argv[1] if len(sys.argv) > 1 else "pandas"
    p = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
    run_benchmark(backend, parallel=p)
