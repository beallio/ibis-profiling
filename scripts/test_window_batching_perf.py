import ibis
import pandas as pd
import numpy as np
import time


def generate_benchmark_data(n_rows=100_000, n_cols=100):
    print(f"Generating {n_rows} rows x {n_cols} columns...")
    data = {f"col_{i}": np.random.randint(0, 1000, size=n_rows) for i in range(n_cols)}
    return pd.DataFrame(data)


def test_batching_perf(n_rows=100_000, n_cols=100):
    df = generate_benchmark_data(n_rows, n_cols)
    con = ibis.duckdb.connect()
    t = con.create_table("bench", df)

    print(f"Starting window-based batching for {n_cols} columns...")
    start_time = time.time()

    # Step 1: Mutate with window functions
    mutates = {}
    for i in range(n_cols):
        col_name = f"col_{i}"
        col = t[col_name]
        # is_singleton = (count over partition == 1)
        # Using win=ibis.window(group_by=col)
        # count(col) excludes nulls by default in most backends
        mutates[f"{col_name}__is_singleton"] = (
            col.count().over(ibis.window(group_by=col)) == 1
        ).cast("int")

    m = t.mutate(mutates)

    # Step 2: Aggregate sums
    aggs = [m[f"col_{i}__is_singleton"].sum().name(f"col_{i}__n_unique") for i in range(n_cols)]
    agg_expr = m.aggregate(aggs)

    print("Executing batched query...")
    results = agg_expr.execute()
    end_time = time.time()

    print(f"Batched query completed in {end_time - start_time:.2f} seconds.")
    print("Sample results:", results.iloc[0, :5].to_dict())


if __name__ == "__main__":
    import sys

    n_cols = 100
    if len(sys.argv) > 1:
        n_cols = int(sys.argv[1])
    test_batching_perf(n_cols=n_cols)
