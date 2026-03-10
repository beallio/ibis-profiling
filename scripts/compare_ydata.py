import ibis
import json
import time
from ibis_profiling import profile

# Note: This script assumes ydata_profiling is available in the environment it's run in.
try:
    from ydata_profiling import ProfileReport as YProfileReport

    YDATA_AVAILABLE = True
except ImportError:
    YDATA_AVAILABLE = False
    print("Warning: ydata-profiling not found. Only Ibis profiling will run.")


def main():
    path = "/home/beallio/Downloads/loan_data_20M.parquet"
    print(f"Loading {path}...")

    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    print("--- Ibis Profiling ---")
    start = time.time()
    ibis_report = profile(table)
    ibis_duration = time.time() - start
    print(f"Ibis Profile completed in {ibis_duration:.2f} seconds.")

    ibis_dict = ibis_report.to_dict()
    with open("ibis_loan_profile.json", "w") as f:
        json.dump(ibis_dict, f, indent=2)

    if YDATA_AVAILABLE:
        print("\n--- ydata-profiling (minimal) ---")
        # ydata needs a pandas dataframe, which might be slow for 20M rows
        # We might want to sample if it takes too long, but let's try the full thing if possible
        # Or just use a subset for parity check if memory is an issue.
        print("Converting to pandas for ydata...")
        df_pandas = table.to_pandas()

        start = time.time()
        ydata_report = YProfileReport(df_pandas, minimal=True, title="ydata Loan Profile")
        ydata_report.to_file("ydata_loan_profile.html")
        ydata_duration = time.time() - start
        print(f"ydata Profile completed in {ydata_duration:.2f} seconds.")

        # Parity Check (Basic)
        print("\n--- Parity Check ---")
        ydata_dict = ydata_report.get_description()

        ibis_row_count = ibis_dict["dataset"]["row_count"]
        ydata_row_count = ydata_dict["table"]["n"]

        print(f"Ibis Row Count: {ibis_row_count}")
        print(f"ydata Row Count: {ydata_row_count}")

        if ibis_row_count == ydata_row_count:
            print("Row count parity: OK")
        else:
            print("Row count parity: FAIL")

        # Check a few columns
        for col in ["loan_amount", "interest_rate"]:
            if col in ibis_dict["columns"] and col in ydata_dict["variables"]:
                i_mean = ibis_dict["columns"][col].get("mean")
                y_mean = ydata_dict["variables"][col].get("mean")
                print(f"Column '{col}' Mean - Ibis: {i_mean}, ydata: {y_mean}")


if __name__ == "__main__":
    main()
