import time
import json
import os
import pandas as pd
from ydata_profiling import ProfileReport


def main():
    path = "loan_data_1M.parquet"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    print(f"Profiling 1 Million Records from {path} with ydata-profiling (Minimal)...")

    df = pd.read_parquet(path)

    start = time.time()
    profile = ProfileReport(df, minimal=True, title="ydata 1M Profile")
    stats = profile.get_description()
    duration = time.time() - start

    print(f"ydata-profiling Duration: {duration:.2f} seconds")

    # Extract some key stats for parity check
    table_stats = stats.table
    var_stats = stats.variables

    out = {
        "n": int(table_stats["n"]),
        "loan_amount_mean": float(var_stats["loan_amount"]["mean"]),
        "interest_rate_mean": float(var_stats["interest_rate"]["mean"]),
    }

    with open("ydata_1M_stats.json", "w") as f:
        json.dump(out, f, indent=2)
    print("ydata stats saved to ydata_1M_stats.json")


if __name__ == "__main__":
    main()
