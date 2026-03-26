import os
import time
import psutil
import ibis
import polars as pl
import numpy as np
from datetime import datetime
from ibis_profiling import profile


def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # MB


def generate_financial_data(n=10_000_000):
    print(f"Generating {n} rows of financial data...")

    # Create base dataframe with numeric/categorical columns
    df = pl.DataFrame(
        {
            "id": np.arange(n, dtype=np.int64),
            "transaction_amount": np.random.uniform(1, 5000, n).astype(np.float64),
            "currency": np.random.choice(["USD", "EUR", "GBP", "JPY"], n),
            "transaction_type": np.random.choice(["Buy", "Sell", "Transfer"], n),
            "account_id": np.random.randint(1000, 9999, n).astype(np.int32),
            "balance_before": np.random.uniform(10000, 100000, n).astype(np.float64),
            "balance_after": np.random.uniform(10000, 100000, n).astype(np.float64),
            "fee": np.random.uniform(0, 50, n).astype(np.float64),
            "is_fraud": np.random.choice([True, False], n, p=[0.01, 0.99]),
            "risk_score": np.random.uniform(0, 1, n).astype(np.float64),
            "customer_age": np.random.randint(18, 90, n).astype(np.int16),
            "department": np.random.choice(["Retail", "Corporate", "Investment"], n),
            "country": np.random.choice(["US", "UK", "DE", "FR", "JP"], n),
            "card_type": np.random.choice(["Visa", "MasterCard", "Amex"], n),
        }
    )

    # Vectorized string formatting and temporal logic
    df = df.with_columns(
        [
            # Timestamp generation: base + random offset in seconds
            (
                pl.lit(datetime(2020, 1, 1))
                + pl.duration(seconds=np.random.randint(0, 31536000, n))
            ).alias("timestamp"),
            # String IDs
            ("M_" + (pl.col("id") % 1000).cast(pl.String)).alias("merchant_id"),
            ("A" + (pl.col("id") % 5000).cast(pl.String)).alias("auth_code"),
            ("REF-" + (pl.col("id") % 100000).cast(pl.String)).alias("reference"),
            ("B" + (pl.col("id") % 100).cast(pl.String)).alias("branch_code"),
            # Conditional notes
            pl.when(pl.col("id") % 5 == 0)
            .then(pl.lit("Special transaction"))
            .otherwise(None)
            .alias("notes"),
        ]
    )

    return ibis.memtable(df)


def run_benchmark(version_label):
    t = generate_financial_data(10_000_000)

    print(f"Starting benchmark for version: {version_label}")
    start_time = time.time()
    start_mem = get_memory_usage()

    # Run full profile with sketches
    profile(t, minimal=False, use_sketches=True)

    end_time = time.time()
    end_mem = get_memory_usage()

    duration = end_time - start_time
    peak_mem = end_mem - start_mem

    print(f"[{version_label}] Duration: {duration:.2f}s")
    print(f"[{version_label}] Memory Delta: {peak_mem:.2f} MB")

    return {"version": version_label, "duration_s": duration, "memory_delta_mb": peak_mem}


if __name__ == "__main__":
    import sys

    label = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    res = run_benchmark(label)

    # Write result to a temporary file for consolidation
    with open(f"/tmp/ibis-profiling/bench_{label}.txt", "w") as f:
        f.write(f"{res['version']},{res['duration_s']},{res['memory_delta_mb']}")
