# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "polars",
#   "pyarrow",
#   "numpy",
#   "faker",
# ]
# ///
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import ibis
import time
from ibis_profiling import ProfileReport


def main():
    data_path = "/tmp/ibis-profiling/loan_data_5M.parquet"

    # 1. Generate 5M records if not present (or force for fresh test)
    if not os.path.exists(data_path):
        print("Generating 5M records with randomized missing values (Vectorized)...")
        from generate_test_data import generate_fast_loan_data

        df = generate_fast_loan_data(5_000_000)
        df.write_parquet(data_path)
        print(f"Data saved to {data_path}")

    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    # 3. Profile
    print("Starting full profile of 5M records (histograms + correlations)...")
    start_time = time.time()
    report = ProfileReport(table, title="Ibis Profiling: 5M Rows Stress Test")
    duration = time.time() - start_time
    print(f"Profile completed in {duration:.2f} seconds.")

    # 4. Export
    out_default = "/tmp/ibis-profiling/profile_5M_default.html"
    out_ydata = "/tmp/ibis-profiling/profile_5M_ydata.html"
    out_json = "/tmp/ibis-profiling/profile_5M.json"

    print("Generating reports...")
    print(f"  - Default: {out_default}")
    report.to_file(out_default, theme="default")

    print(f"  - YData-like: {out_ydata}")
    report.to_file(out_ydata, theme="ydata-like")

    print(f"  - JSON: {out_json}")
    report.to_file(out_json)

    print("Done!")


if __name__ == "__main__":
    # Ensure generate_test_data is importable
    import sys

    sys.path.append(os.path.dirname(__file__))
    main()
