import ibis
import time
import os
import sys
from ibis_profiling import ProfileReport

# Add scripts directory to path for generate_test_data
sys.path.append(os.path.dirname(__file__))
from generate_test_data import generate_fast_loan_data


def main():
    data_path = "/tmp/ibis-profiling/loan_data_5M.parquet"
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    # 1. Generate or load 5M records
    if not os.path.exists(data_path):
        print("Generating 5M records...")
        df = generate_fast_loan_data(5_000_000)
        df.write_parquet(data_path)
        print(f"Data saved to {data_path}")
    else:
        print(f"Using existing data: {data_path}")

    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    # 2. Profile
    print("Starting full profile of 5M records...")
    start_time = time.time()
    # Using monotonicity_order_by if available in the dataset (id exists)
    report = ProfileReport(table, monotonicity_order_by="id")
    duration = time.time() - start_time
    print(f"Profile completed in {duration:.2f} seconds.")

    # 3. Export Default
    out_default = "/tmp/ibis-profiling/profile_5M_default.html"
    print(f"Exporting 'default' theme to {out_default}...")
    report.to_file(out_default, theme="default")

    # 4. Export YData-like
    out_ydata = "/tmp/ibis-profiling/profile_5M_ydata.html"
    print(f"Exporting 'ydata-like' theme to {out_ydata}...")
    report.to_file(out_ydata, theme="ydata-like")

    print("\nGeneration Complete!")
    print(f"Default: {out_default} ({os.path.getsize(out_default) / 1024:.2f} KB)")
    print(f"YData:   {out_ydata} ({os.path.getsize(out_ydata) / 1024:.2f} KB)")


if __name__ == "__main__":
    main()
