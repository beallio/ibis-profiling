import os
import time
import psutil
import ibis
import polars as pl
import numpy as np
from datetime import datetime, timedelta
from ibis_profiling import profile


def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # MB


def generate_financial_data(n=10_000_000):
    print(f"Generating {n} rows of financial data...")

    # Use numpy/polars for fast generation
    data = {
        "id": np.arange(n),
        "transaction_amount": np.random.uniform(1, 5000, n),
        "currency": np.random.choice(["USD", "EUR", "GBP", "JPY"], n),
        "transaction_type": np.random.choice(["Buy", "Sell", "Transfer"], n),
        "account_id": np.random.randint(1000, 9999, n),
        "timestamp": [
            datetime(2020, 1, 1) + timedelta(seconds=int(i))
            for i in np.random.randint(0, 31536000, n)
        ],
        "balance_before": np.random.uniform(10000, 100000, n),
        "balance_after": np.random.uniform(10000, 100000, n),
        "fee": np.random.uniform(0, 50, n),
        "is_fraud": np.random.choice([True, False], n, p=[0.01, 0.99]),
        "merchant_id": [f"M_{i % 1000}" for i in range(n)],
        "country": np.random.choice(["US", "UK", "DE", "FR", "JP"], n),
        "card_type": np.random.choice(["Visa", "MasterCard", "Amex"], n),
        "auth_code": [f"A{i % 5000}" for i in range(n)],
        "reference": [f"REF-{i % 100000}" for i in range(n)],
        "risk_score": np.random.uniform(0, 1, n),
        "customer_age": np.random.randint(18, 90, n),
        "department": np.random.choice(["Retail", "Corporate", "Investment"], n),
        "branch_code": [f"B{i % 100}" for i in range(n)],
        "notes": [None if i % 5 != 0 else "Special transaction" for i in range(n)],
    }

    df = pl.DataFrame(data)
    return ibis.memtable(df)


def run_benchmark(version_label):
    t = generate_financial_data(10_000_000)

    print(f"Starting benchmark for version: {version_label}")
    start_time = time.time()
    start_mem = get_memory_usage()

    # Run full profile
    profile(t, minimal=False)

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
