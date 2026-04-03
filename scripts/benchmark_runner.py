# /// script
# dependencies = [
#   "psutil",
# ]
# ///
import os
import subprocess
import json


def run_cmd(cmd):
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.stdout


def main():
    # Matrix definition
    rows_list = [1_000_000, 10_000_000]  # Simplified for initial run
    cols_list = [10, 50]
    batches = [5, 50, 500]

    bench_dir = "/tmp/ibis-profiling/bench"
    results_dir = "/tmp/ibis-profiling/results"
    os.makedirs(bench_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    final_results = []

    python_exe = f"{os.environ.get('VIRTUAL_ENV', '.venv')}/bin/python"

    for rows in rows_list:
        for cols in cols_list:
            data_path = f"{bench_dir}/data_{rows}_{cols}.parquet"

            # Step 1: Generate Data (if not exists)
            if not os.path.exists(data_path):
                print(f"--- Generating {rows}x{cols} ---")
                run_cmd(
                    [
                        python_exe,
                        "scripts/generate_bench_data_varied.py",
                        str(rows),
                        str(cols),
                        data_path,
                    ]
                )

            for batch in batches:
                print(f"--- Benchmarking: {rows} rows, {cols} cols, {batch} batch_size ---")
                res_file = f"{results_dir}/res_{rows}_{cols}_{batch}.json"

                # Step 2: Run Benchmark in separate process
                # We use a large timeout for 20M+ runs
                try:
                    subprocess.run(
                        [
                            python_exe,
                            "scripts/benchmark_worker.py",
                            data_path,
                            str(batch),
                            res_file,
                        ],
                        timeout=600,  # 10 minutes max per case
                    )
                except subprocess.TimeoutExpired:
                    print(f"Timeout expired for {rows}x{cols} with batch {batch}")
                    continue

                # Step 3: Collect Results
                if os.path.exists(res_file):
                    with open(res_file, "r") as f:
                        case_res = json.load(f)
                        case_res.update(
                            {
                                "rows": rows,
                                "cols": cols,
                                "batch_size": batch,
                                "total_cells": rows * cols,
                            }
                        )
                        final_results.append(case_res)
                        print(
                            f"Success: {case_res['duration']:.2f}s, Peak: {case_res['peak_rss_mb']:.2f} MB"
                        )
                else:
                    print("Worker failed to produce results (likely OOM).")
                    final_results.append(
                        {
                            "rows": rows,
                            "cols": cols,
                            "batch_size": batch,
                            "status": "OOM/Killed",
                            "total_cells": rows * cols,
                        }
                    )

    # Save final report
    with open("docs/performance_benchmark_matrix.json", "w") as f:
        json.dump(final_results, f, indent=2)

    print("\n--- Benchmark Complete ---")
    print("Results saved to docs/performance_benchmark_matrix.json")


if __name__ == "__main__":
    main()
