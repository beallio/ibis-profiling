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
from ibis_profiling import ProfileReport


def main():
    data_path = "/tmp/ibis-profiling/loan_data_5M.parquet"

    # 1. Get 5M records (Use existing 20M file if available to save time)
    source_20M = "/home/beallio/Downloads/loan_data_20M.parquet"
    if os.path.exists(source_20M):
        print(f"Sampling 5M records from {source_20M}...")
        con = ibis.duckdb.connect()
        table = con.read_parquet(source_20M).limit(5_000_000)
    elif not os.path.exists(data_path):
        print("Generating 5M records (Faker is slow, this may take a minute)...")
        from generate_test_data import generate_legacy_loan_data
        from faker import Faker

        fake = Faker()
        df = generate_legacy_loan_data(fake, 5_000_000)
        df.write_parquet(data_path)
        print(f"Data saved to {data_path}")
        con = ibis.duckdb.connect()
        table = con.read_parquet(data_path)
    else:
        con = ibis.duckdb.connect()
        table = con.read_parquet(data_path)

    # 3. Profile
    print("Starting full profile of 5M records (histograms + correlations)...")
    start_time = time.time()
    report = ProfileReport(table)
    duration = time.time() - start_time
    print(f"Profile completed in {duration:.2f} seconds.")

    # 4. Export
    out_html = "/tmp/ibis-profiling/profile_5M.html"
    out_json = "/tmp/ibis-profiling/profile_5M.json"

    print("Generating reports...")
    report.to_file(out_html)
    report.to_file(out_json)

    print("Done!")
    print(f"HTML: {out_html}")
    print(f"JSON: {out_json}")


if __name__ == "__main__":
    # Ensure generate_test_data is importable if needed
    import sys

    sys.path.append(os.path.dirname(__file__))
    main()
