import ibis
import pandas as pd
import numpy as np
import os
from ibis_profiling import ProfileReport


def generate_financial_data():
    output_dir = "/tmp/ibis-profiling/sample_reports"
    os.makedirs(output_dir, exist_ok=True)

    n = 1_100_000
    print(f"Generating financial stress dataset ({n:,} rows) with more alerts...")

    # Financial-like features
    data = {
        "account_id": np.arange(n),
        "balance": np.random.exponential(5000, n),
        "income": np.random.lognormal(10, 0.5, n),
        "credit_score": np.random.randint(300, 850, n),
        "debt_ratio": np.random.beta(2, 5, n),
        "transaction_count": np.random.poisson(20, n),
        "is_fraud": np.random.choice([0, 1], n, p=[0.99, 0.01]),
        "region": np.random.choice(["North", "South", "East", "West", "Central"], n),
        "account_type": np.random.choice(["Savings", "Checking", "Investment", "Loan"], n),
        "last_login_days": np.random.randint(0, 365, n),
        "monthly_spend": np.random.normal(2000, 800, n).clip(0),
        "age": np.random.randint(18, 95, n),
        "referral_bonus": np.random.choice([0, 25, 50, 100], n),
        "utilization_rate": np.random.uniform(0, 1, n),
        "tenure_months": np.random.geometric(0.02, n),
    }

    # --- Data to trigger more alerts ---

    # 1. Constant column
    data["constant_val"] = ["FIXED_VALUE"] * n

    # 2. Skewed column
    data["highly_skewed"] = np.random.pareto(1, n) * 100

    # 3. Zeros-heavy column
    data["mostly_zeros"] = np.random.choice([0, 1, 2], n, p=[0.95, 0.025, 0.025])

    # 4. Missing-heavy column
    data["mostly_missing"] = np.random.choice([np.nan, 1.0, 2.0], n, p=[0.8, 0.1, 0.1])

    # 5. High Cardinality Categorical
    data["user_agent_hash"] = [f"UA_{i % (n // 2)}" for i in range(n)]

    # 6. Uniform floats (Should NOT trigger UNIQUE alert now)
    data["random_noise"] = np.random.uniform(0, 1, n)

    # Inject correlations
    # Balance strongly correlated with Income
    data["balance"] = data["income"] * 0.4 + np.random.normal(0, 1000, n)
    # Utilization strongly correlated with Debt Ratio
    data["utilization_rate"] = data["debt_ratio"] * 0.7 + np.random.uniform(0, 0.3, n)

    df = pd.DataFrame(data)
    con = ibis.duckdb.connect()
    table = con.create_table("financial_data_v3", df)

    print("Generating Financial Reports (v0.1.7)...")
    ProfileReport(table, title="Financial Dataset: Alert Stress Test v0.1.7").to_file(
        os.path.join(output_dir, "financial_alerts_default.html")
    )
    ProfileReport(table, title="Financial Dataset: Alert Stress Test v0.1.7").to_file(
        os.path.join(output_dir, "financial_alerts_ydata.html"), theme="ydata-like"
    )

    print(f"\nFinancial reports generated in '{output_dir}'")


if __name__ == "__main__":
    generate_financial_data()
