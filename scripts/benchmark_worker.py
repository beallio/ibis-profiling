# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "psutil",
#   "pyarrow",
# ]
# ///
import os
import sys
import time
import json
import psutil
import ibis
from ibis_profiling import ProfileReport


def get_mem_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def run_benchmark_worker(data_path, batch_size, result_path):
    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    start_time = time.time()
    peak_mem = 0

    def on_progress(inc, label):
        nonlocal peak_mem
        mem = get_mem_mb()
        if mem > peak_mem:
            peak_mem = mem

    try:
        report = ProfileReport(
            table,
            minimal=False,
            parallel=False,
            global_batch_size=batch_size,
            on_progress=on_progress,
        )
        duration = time.time() - start_time

        # Save results
        results = {
            "duration": duration,
            "peak_rss_mb": peak_mem,
            "status": "success",
            "metrics": {
                "infrastructure": report.analysis.get("performance", {}).get("Infrastructure", 0),
                "global_aggregates": report.analysis.get("performance", {}).get(
                    "Global Aggregates", 0
                ),
                "advanced_pass": report.analysis.get("performance", {}).get("Advanced Pass", 0),
                "complex_pass": report.analysis.get("performance", {}).get("Complex Pass", 0),
                "correlations": report.analysis.get("performance", {}).get("Correlations", 0),
            },
        }
    except Exception as e:
        results = {"status": "failed", "error": str(e), "peak_rss_mb": peak_mem}

    with open(result_path, "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)

    data_path = sys.argv[1]
    batch_size = int(sys.argv[2])
    result_path = sys.argv[3]

    run_benchmark_worker(data_path, batch_size, result_path)
