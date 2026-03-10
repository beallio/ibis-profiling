import ibis
import json
import time
import os
from ibis_profiling import profile

# Check for ydata-profiling
try:
    from ydata_profiling import ProfileReport as YProfileReport

    YDATA_AVAILABLE = True
except ImportError:
    YDATA_AVAILABLE = False


def compare_metrics(i_dict, y_dict):
    """Basic comparison of metrics for parity."""
    print("\n--- Metric Parity Check (Ibis vs. ydata) ---")

    i_row_count = i_dict["dataset"]["row_count"]
    y_row_count = y_dict["table"]["n"]
    print(
        f"Dataset Row Count: Ibis: {i_row_count}, ydata: {y_row_count} (Parity: {i_row_count == y_row_count})"
    )

    # Check numeric columns
    for col in ["loan_amount", "interest_rate", "credit_score"]:
        if col in i_dict["columns"] and col in y_dict["variables"]:
            i_stats = i_dict["columns"][col]
            y_stats = y_dict["variables"][col]

            i_mean = i_stats.get("mean")
            y_mean = y_stats.get("mean")
            i_min = i_stats.get("min")
            y_min = y_stats.get("min")

            print(f"Column '{col}':")
            print(
                f"  Mean: Ibis: {i_mean:.4f}, ydata: {y_mean:.4f} (Diff: {abs(i_mean - y_mean):.6f})"
            )
            print(f"  Min:  Ibis: {i_min}, ydata: {y_min} (Parity: {i_min == y_min})")


def main():
    path = "loan_data_5M.parquet"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    # Use DuckDB as the backend
    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    print(f"Profiling 5 Million Records from {path}...")

    # 1. Ibis Profiling
    print("\n--- Running Ibis Profiler ---")
    start = time.time()
    ibis_report = profile(table)
    ibis_duration = time.time() - start
    print(f"Ibis Profiler Duration: {ibis_duration:.2f} seconds")

    # 2. ydata-profiling
    if YDATA_AVAILABLE:
        print("\n--- Running ydata-profiling (Minimal) ---")
        # ydata needs a pandas dataframe
        print("Converting to pandas for ydata...")
        df_pandas = table.to_pandas()

        start = time.time()
        ydata_report = YProfileReport(df_pandas, minimal=True, title="ydata 5M Profile")
        # Generate some internal stats for comparison
        ydata_dict = ydata_report.get_description()
        ydata_duration = time.time() - start
        print(f"ydata-profiling Duration: {ydata_duration:.2f} seconds")

        # 3. Compare Results
        compare_metrics(ibis_report.to_dict(), ydata_dict)

        print(f"\nSummary: Ibis was {ydata_duration / ibis_duration:.1f}x faster.")
    else:
        print("\nydata-profiling is not available in this environment.")
        print("Finalizing results for Ibis profiling:")
        print(json.dumps(ibis_report.to_dict()["dataset"], indent=2))


if __name__ == "__main__":
    main()
