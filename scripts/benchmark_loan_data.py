import ibis
import time
import json
from ibis_profiling import profile


def main():
    path = "/home/beallio/Downloads/loan_data_20M.parquet"
    print(f"Loading {path}...")

    # Use DuckDB as the backend for the parquet file
    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    print("Starting profile...")
    start_time = time.time()

    report = profile(table)

    end_time = time.time()
    duration = end_time - start_time

    print(f"Profile completed in {duration:.2f} seconds.")

    # Save reports
    with open("loan_profile.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    with open("loan_profile.html", "w") as f:
        f.write(report.to_html())

    print("Reports saved to loan_profile.json and loan_profile.html")


if __name__ == "__main__":
    main()
