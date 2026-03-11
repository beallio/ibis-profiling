# /// script
# dependencies = [
#   "polars",
#   "faker",
#   "pyarrow",
#   "numpy",
# ]
# ///
import polars as pl
import numpy as np
from faker import Faker
import argparse
import os


def generate_fast_loan_data(n_rows):
    """Vectorized generation of loan data for high performance."""
    rng = np.random.default_rng()
    fake = Faker()

    data = {
        "loan_id": np.arange(n_rows),
        "customer_id": rng.integers(100000, 999999, size=n_rows),
        "loan_amount": rng.uniform(5000, 50000, size=n_rows),
        "interest_rate": rng.uniform(0.05, 0.25, size=n_rows),
        "term_months": rng.choice([12, 24, 36, 48, 60, 72, 84], size=n_rows),
        "credit_score": rng.integers(300, 850, size=n_rows),
        "annual_income": rng.uniform(30000, 200000, size=n_rows),
        "dti_ratio": rng.uniform(0.1, 0.5, size=n_rows),
        "is_secured": rng.choice([True, False], size=n_rows),
        "loan_status": rng.choice(["Current", "Fully Paid", "Late", "Default"], size=n_rows),
        "region": rng.choice(["West", "Midwest", "South", "Northeast"], size=n_rows),
    }

    df = pl.DataFrame(data)

    # Add a few string columns using Faker (still a bit slow, but only for 2 columns)
    if n_rows <= 100000:
        df = df.with_columns(
            [
                pl.Series("city", [fake.city() for _ in range(n_rows)]),
                pl.Series("employer", [fake.company() for _ in range(n_rows)]),
            ]
        )
    else:
        # For very large sets, reuse a pool of strings to stay fast
        pool_size = 10000
        cities = [fake.city() for _ in range(pool_size)]
        employers = [fake.company() for _ in range(pool_size)]
        df = df.with_columns(
            [
                pl.Series("city", rng.choice(cities, size=n_rows)),
                pl.Series("employer", rng.choice(employers, size=n_rows)),
            ]
        )

    return df


def main():
    parser = argparse.ArgumentParser(description="High-performance data generator.")
    parser.add_argument("--rows", type=int, default=100000)
    parser.add_argument("--output", type=str, default="/tmp/ibis-profiling/loan_data.parquet")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    print(f"Generating {args.rows:,} rows...")
    df = generate_fast_loan_data(args.rows)
    df.write_parquet(args.output)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
