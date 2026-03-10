import ibis
import time
import json
import os
from ibis_profiling import profile


def main():
    # Use environment variable or default
    data_path = os.getenv("LOAN_DATA_PATH", "/home/beallio/Downloads/loan_data_20M.parquet")
    output_dir = os.getenv("IBIS_PROFILING_TMP", "/tmp/ibis-profiling")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    print(f"Loading {data_path}...")

    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    print("Starting Ibis profile...")
    start_time = time.time()
    report = profile(table)
    duration = time.time() - start_time

    print(f"Profile completed in {duration:.2f} seconds.")

    # Save reports to /tmp
    json_path = os.path.join(output_dir, "loan_profile.json")
    html_path = os.path.join(output_dir, "loan_profile.html")

    with open(json_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    with open(html_path, "w") as f:
        f.write(report.to_html())

    print(f"Reports saved to {json_path} and {html_path}")


if __name__ == "__main__":
    main()
