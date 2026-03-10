import ibis
import time
import json
import os
from ibis_profiling import profile


def main():
    path = "loan_data_1M.parquet"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    print(f"Profiling 1 Million Records from {path} with Ibis Profiler...")

    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    start = time.time()
    report = profile(table)
    duration = time.time() - start

    print(f"Ibis Profiler Duration: {duration:.2f} seconds")

    ibis_dict = report.to_dict()
    out = {
        "n": int(ibis_dict["dataset"]["row_count"]),
        "loan_amount_mean": float(ibis_dict["columns"]["loan_amount"]["mean"]),
        "interest_rate_mean": float(ibis_dict["columns"]["interest_rate"]["mean"]),
    }

    with open("ibis_1M_stats.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Ibis stats saved to ibis_1M_stats.json")


if __name__ == "__main__":
    main()
