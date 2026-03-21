import ibis
import pandas as pd
import numpy as np
from ibis_profiling import profile
import os
import time


def generate_financial_data_chunk(n, start_idx, rng):
    """Generates a chunk of financial data."""
    data = {
        "tx_id": np.arange(start_idx, start_idx + n),
        "account_id": [f"ACC_{i % 100000}" for i in range(start_idx, start_idx + n)],
        "amount": rng.normal(500, 200, n),
        "balance": rng.uniform(1000, 100000, n),
        "is_fraud": rng.choice([0, 1], size=n, p=[0.99, 0.01]),
        "merchant_cat": rng.choice(
            ["Retail", "Food", "Travel", "Health", "Service", "Other"], size=n
        ),
        "days_since_tx": rng.integers(0, 60, size=n).astype(float),
        "lat": rng.uniform(-90, 90, n),
        "lon": rng.uniform(-180, 180, n),
        "is_online": rng.choice([True, False], size=n),
        "currency": rng.choice(["USD", "EUR", "GBP", "JPY"], size=n),
        "risk_score": rng.uniform(0, 1, n),
        "auth_code": [f"AUTH_{rng.integers(1000, 9999)}" for _ in range(n)],
        "terminal_id": [f"TERM_{rng.integers(1, 5000)}" for _ in range(n)],
        "tx_type": rng.choice(["Debit", "Credit", "Transfer"], size=n),
        "vendor": rng.choice(["Stripe", "Square", "PayPal", "Bank"], size=n),
        "is_recurring": rng.choice([0, 1], size=n, p=[0.8, 0.2]),
        "fee": rng.uniform(0, 5, n),
        "discount": rng.uniform(0, 50, n),
        "user_age": rng.integers(18, 90, size=n).astype(float),
    }

    # Introduce some missingness
    # 5% missing in amount
    mask_amount = rng.random(n) < 0.05
    data["amount"][mask_amount] = np.nan

    # 3% missing in balance
    mask_balance = rng.random(n) < 0.03
    data["balance"][mask_balance] = np.nan

    # 2% missing in days_since_tx
    mask_days = rng.random(n) < 0.02
    data["days_since_tx"][mask_days] = np.nan
    return pd.DataFrame(data)


def main():
    total_rows = 20_000_000
    chunk_size = 2_000_000
    output_dir = "/tmp/ibis-profiling/20M_financial"
    data_path = os.path.join(output_dir, "data.parquet")
    os.makedirs(output_dir, exist_ok=True)

    rng = np.random.default_rng(42)

    if not os.path.exists(data_path):
        print(f"Generating {total_rows:,} rows of financial data in chunks...")
        for i in range(0, total_rows, chunk_size):
            n = min(chunk_size, total_rows - i)
            print(f"  Generating chunk {i // chunk_size + 1}...")
            df = generate_financial_data_chunk(n, i, rng)

            chunk_path = f"{data_path}.chunk{i // chunk_size}"
            df.to_parquet(chunk_path)

        print("Combining chunks into a single Parquet file using Ibis/DuckDB...")
        con = ibis.duckdb.connect()
        table = con.read_parquet(f"{data_path}.chunk*")
        table.to_parquet(data_path)

        # Cleanup chunks
        import glob

        for f in glob.glob(f"{data_path}.chunk*"):
            os.remove(f)
    else:
        print(f"Data already exists at {data_path}")

    # Now profile it
    print("\nConnecting to data with Ibis...")
    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    print(f"Starting profile of {total_rows:,} rows x 20 columns...")
    start_time = time.time()

    # Use full profile
    print("Starting FULL profile...")
    report = profile(table, minimal=False, title="20M Financial Transactions Audit")

    duration = time.time() - start_time
    print(f"Profile completed in {duration:.2f} seconds.")

    print("Writing reports...")
    html_path = os.path.join(output_dir, "report_20M.html")
    json_path = os.path.join(output_dir, "report_20M.json")

    report.to_file(html_path)
    report.to_file(json_path)

    print(f"Reports saved to: {output_dir}")


if __name__ == "__main__":
    main()
