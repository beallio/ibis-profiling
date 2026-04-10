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


def generate_customer_data(n_rows):
    """Vectorized generation of customer data."""
    rng = np.random.default_rng(42)
    fake = Faker()

    # Pre-generate some string pools for speed
    pool_size = min(10000, n_rows // 100 + 1)
    cities = [fake.city() for _ in range(pool_size)]
    states = [fake.state_abbr() for _ in range(pool_size)]
    street_names = [fake.street_name() for _ in range(pool_size)]
    companies = [fake.company() for _ in range(pool_size)]
    job_titles = [fake.job() for _ in range(pool_size)]
    emails_domains = ["example.com", "test.org", "gmail.com", "yahoo.com", "outlook.com"]

    data = {
        "customer_id": np.arange(n_rows),
        "age": rng.integers(18, 90, size=n_rows),
        "credit_score": rng.integers(300, 850, size=n_rows),
        "annual_income": rng.uniform(20000, 250000, size=n_rows),
        "tenure_months": rng.integers(0, 240, size=n_rows),
        "is_active": rng.choice([True, False], size=n_rows),
        "account_balance": rng.uniform(0, 1000000, size=n_rows),
        "num_transactions": rng.integers(0, 500, size=n_rows),
        "last_login_days": rng.integers(0, 365, size=n_rows),
        "loyalty_points": rng.integers(0, 10000, size=n_rows),
        # String columns from pools
        "city": rng.choice(cities, size=n_rows),
        "state": rng.choice(states, size=n_rows),
        "street": rng.choice(street_names, size=n_rows),
        "company": rng.choice(companies, size=n_rows),
        "job_title": rng.choice(job_titles, size=n_rows),
        "email_domain": rng.choice(emails_domains, size=n_rows),
        # Some categorical columns
        "gender": rng.choice(
            ["Male", "Female", "Other", None], size=n_rows, p=[0.48, 0.48, 0.02, 0.02]
        ),
        "education": rng.choice(
            ["High School", "Bachelors", "Masters", "PhD", "None"], size=n_rows
        ),
        "risk_category": rng.choice(["Low", "Medium", "High"], size=n_rows),
        "preferred_channel": rng.choice(["Email", "SMS", "Phone", "In-person"], size=n_rows),
    }

    df = pl.DataFrame(data)

    # Inject nulls randomly (0% to 5%)
    for col in df.columns:
        if col == "customer_id":
            continue
        p_missing = rng.uniform(0, 0.05)
        null_mask = rng.random(n_rows) < p_missing
        df = df.with_columns(
            pl.when(pl.Series(null_mask)).then(None).otherwise(pl.col(col)).alias(col)
        )

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate 10M rows of 20-column customer data.")
    parser.add_argument("--rows", type=int, default=10000000)
    parser.add_argument(
        "--output", type=str, default="/tmp/ibis-profiling/10M_20col_customer_data.parquet"
    )
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    print(f"Generating {args.rows:,} rows of customer data...")
    df = generate_customer_data(args.rows)
    df.write_parquet(args.output)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
