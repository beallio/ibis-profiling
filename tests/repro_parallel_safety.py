import ibis
from ibis_profiling import ProfileReport
import numpy as np
import pandas as pd


def test_parallel_execution_safety():
    """
    Tests if parallel execution with DuckDB is stable.
    Note: DuckDB is actually quite good at thread safety on a single connection for *read* operations
    if the underlying driver is configured correctly, but sharing a single connection object across
    threads in many Python DB-API drivers is technically discouraged or unsafe.

    This test attempts to trigger race conditions or inconsistencies by running many complex
    parallel queries on a small dataset.
    """
    # Create a dataset that forces many complex metrics (histograms, etc.)
    num_cols = 10
    n = 1000
    data = {f"col_{i}": np.random.normal(0, 1, n) for i in range(num_cols)}
    df = pd.DataFrame(data)

    table = ibis.memtable(df)

    # Run once to verify stability
    report = ProfileReport(table, parallel=True, pool_size=4, minimal=False)
    d = report.to_dict()
    assert "variables" in d
    assert len(d["variables"]) == num_cols


if __name__ == "__main__":
    test_parallel_execution_safety()
