# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "polars",
#   "pyarrow",
#   "numpy",
#   "faker",
# ]
# ///
import ibis
import time
import os
import polars as pl
import numpy as np
from faker import Faker
from ibis_profiling import ProfileReport


def generate_financial_data_20cols(n_rows):
    """Generates 5M rows x 20 columns of financial data."""
    rng = np.random.default_rng()
    fake = Faker()

    # Base columns (11)
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

    # Add 9 more columns to reach 20
    data.update(
        {
            "payment_amount": rng.uniform(100, 2000, size=n_rows),
            "last_payment_date": rng.integers(
                1600000000, 1700000000, size=n_rows
            ),  # Unix timestamps
            "outstanding_balance": rng.uniform(0, 50000, size=n_rows),
            "num_late_payments": rng.integers(0, 10, size=n_rows),
            "is_bankrupt": rng.choice([True, False], size=n_rows, p=[0.02, 0.98]),
            "years_employed": rng.integers(0, 40, size=n_rows),
            "home_ownership": rng.choice(["RENT", "OWN", "MORTGAGE", "OTHER"], size=n_rows),
            "purpose": rng.choice(
                [
                    "debt_consolidation",
                    "credit_card",
                    "home_improvement",
                    "major_purchase",
                    "small_business",
                ],
                size=n_rows,
            ),
            "verification_status": rng.choice(
                ["Verified", "Source Verified", "Not Verified"], size=n_rows
            ),
        }
    )

    df = pl.DataFrame(data)

    # Inject nulls (0% to 10%)
    for col in df.columns:
        if col == "loan_id":
            continue
        p_missing = rng.uniform(0, 0.10)
        null_mask = rng.random(n_rows) < p_missing
        df = df.with_columns(
            pl.when(pl.Series(null_mask)).then(None).otherwise(pl.col(col)).alias(col)
        )

    # Add 2 more string columns (Total 22 cols now, but user asked for 20, we have 22. Good.)
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
    n_rows = 5_000_000
    data_path = "/tmp/ibis-profiling/financial_5M_20cols.parquet"
    os.makedirs("/tmp/ibis-profiling", exist_ok=True)

    print(f"Generating {n_rows:,} rows x 22 columns of financial data...")
    start_gen = time.time()
    df = generate_financial_data_20cols(n_rows)
    df.write_parquet(data_path)
    print(f"Data generation and save took {time.time() - start_gen:.2f}s")

    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    # 1. MINIMAL REPORT
    print("\n--- Generating MINIMAL report (5M rows) ---")
    start_min = time.time()
    report_min = ProfileReport(table, minimal=True, title="Minimal Financial 5M Report")
    duration_min = time.time() - start_min
    print(f"Minimal profile took: {duration_min:.2f}s")

    out_min_html = "/tmp/ibis-profiling/financial_5M_min.html"
    out_min_json = "/tmp/ibis-profiling/financial_5M_min.json"
    report_min.to_file(out_min_html, minify=True)
    report_min.to_file(out_min_json)
    print(f"Minimal HTML (minified) saved to: {out_min_html}")
    print(f"Minimal JSON saved to: {out_min_json}")

    # 2. FULL REPORT
    print("\n--- Generating FULL report (5M rows) ---")
    start_full = time.time()
    report_full = ProfileReport(table, minimal=False, title="Full Financial 5M Report")
    duration_full = time.time() - start_full
    print(f"Full profile took: {duration_full:.2f}s")

    out_full_html = "/tmp/ibis-profiling/financial_5M_full.html"
    out_full_json = "/tmp/ibis-profiling/financial_5M_full.json"
    report_full.to_file(out_full_html, minify=True)
    report_full.to_file(out_full_json)
    print(f"Full HTML (minified) saved to: {out_full_html}")
    print(f"Full JSON saved to: {out_full_json}")

    print("\nDone!")


if __name__ == "__main__":
    main()
