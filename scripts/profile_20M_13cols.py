# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "psutil",
#   "pyarrow",
# ]
# ///
import ibis
import time
import os
import psutil
from ibis_profiling import ProfileReport


def get_mem_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def main():
    data_path = "/tmp/ibis-profiling/data_20M_13cols.parquet"
    report_path = "/tmp/ibis-profiling/report_20M_13cols.html"

    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}. Please run generation script first.")
        return

    print(f"[{get_mem_mb():.2f} MB] Connecting to data with Ibis/DuckDB...")
    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    start_prof = time.time()

    def on_progress(inc, label):
        if label:
            print(f"[{time.time() - start_prof:.2f}s][{get_mem_mb():.2f} MB] {label}")

    print("--- Profiling 20M rows x 13 columns (Minimal: False) ---")
    try:
        report = ProfileReport(
            table,
            minimal=False,
            parallel=False,
            on_progress=on_progress,
            title="20M Rows x 13 Columns Performance Test",
        )
        duration_prof = time.time() - start_prof
        print(f"Profiling took: {duration_prof:.2f}s")

        print(f"Saving report to {report_path}...")
        report.to_file(report_path, minify=True)
        print("Report saved successfully.")
    except Exception as e:
        print(f"Profiling FAILED: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
