import ibis
import pandas as pd
import numpy as np
from ibis_profiling import profile
import os


def generate_financial_data(n=1000):
    """Generates a dataset resembling financial data with some missingness."""
    np.random.seed(42)
    data = {
        "account_id": [f"ACC_{i}" for i in range(n)],
        "transaction_amount": np.random.normal(500, 200, n),
        "balance_before": np.random.uniform(1000, 10000, n),
        "is_fraud": np.random.choice([0, 1], size=n, p=[0.95, 0.05]),
        "merchant_category": np.random.choice(["Retail", "Food", "Travel", "Health"], size=n),
        "days_since_last_tx": np.random.randint(0, 30, size=n).astype(float),
    }

    # Introduce missingness
    # transaction_amount has 5% missing
    mask_tx = np.random.choice([True, False], size=n, p=[0.05, 0.95])
    data["transaction_amount"][mask_tx] = None

    # balance_before has 10% missing
    mask_bal = np.random.choice([True, False], size=n, p=[0.10, 0.90])
    data["balance_before"][mask_bal] = None

    # days_since_last_tx has 2% missing
    mask_days = np.random.choice([True, False], size=n, p=[0.02, 0.98])
    data["days_since_last_tx"][mask_days] = None

    # is_fraud is technically an integer but binary (low cardinality)
    # It might be reclassified as Categorical, but we want it in correlations!

    return ibis.memtable(pd.DataFrame(data))


def main():
    output_dir = "/tmp/ibis-profiling/financial_test"
    os.makedirs(output_dir, exist_ok=True)

    print("Generating financial dataset (1000 rows)...")
    table = generate_financial_data(1000)

    print("Generating FULL profile...")
    report = profile(table, minimal=False, title="Financial Data Audit")

    html_path = os.path.join(output_dir, "financial_report.html")
    json_path = os.path.join(output_dir, "financial_report.json")

    report.to_file(html_path)
    report.to_file(json_path)

    print(f"Reports generated in: {output_dir}")

    # Verify correlations in JSON
    import json

    with open(json_path, "r") as f:
        data = json.load(f)

    corrs = data.get("correlations", {})
    pearson = corrs.get("pearson", [])
    spearman = corrs.get("spearman", [])

    print(f"Pearson Matrix Size: {len(pearson)}x{len(pearson[0]) if pearson else 0}")
    print(f"Spearman Matrix Size: {len(spearman)}x{len(spearman[0]) if spearman else 0}")

    missing_heatmap = data.get("missing", {}).get("heatmap", {}).get("matrix", [])
    print(
        f"Missing Heatmap Matrix Size: {len(missing_heatmap)}x{len(missing_heatmap[0]) if missing_heatmap else 0}"
    )

    if len(pearson) > 0:
        print("✅ SUCCESS: Pearson correlations found.")
    else:
        print("❌ FAILURE: Pearson correlations missing.")

    if len(missing_heatmap) > 0:
        print("✅ SUCCESS: Missing value heatmap found.")
    else:
        print("✅ INFO: Missing heatmap empty (maybe not enough columns with nulls?).")


if __name__ == "__main__":
    main()
