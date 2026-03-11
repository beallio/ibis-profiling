import os
import time
import tracemalloc
import argparse
import json
import ibis
import gc
from ibis_profiling import ProfileReport as IbisProfileReport
from ydata_profiling import ProfileReport as YDataProfileReport

# Updated Sizes
SIZES = [10_000, 25_000, 50_000, 500_000, 1_000_000, 5_000_000, 10_000_000, 20_000_000]
PROFILERS = ["ibis", "ydata"]


def run_benchmark(size, profiler, mode, data_path, output_dir):
    print(f"\n--- Running {profiler} ({mode}) for {size:,} rows ---")

    # Force GC before starting
    gc.collect()

    # Load data
    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    # For ydata, we need pandas
    if profiler == "ydata":
        df = table.to_pandas()
    else:
        df = table

    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        if profiler == "ibis":
            report = IbisProfileReport(df, minimal=(mode == "minimal"))
        else:
            report = YDataProfileReport(df, minimal=(mode == "minimal"), progress_bar=False)

        # Trigger computation/rendering
        html_path = os.path.join(output_dir, f"{profiler}_{mode}.html")
        json_path = os.path.join(output_dir, f"{profiler}_{mode}.json")

        report.to_file(html_path)
        report.to_file(json_path)

        duration = time.perf_counter() - start_time
        _, peak_memory = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
        # Cleanup
        del df
        del table
        con.disconnect()
        gc.collect()

    print(f"Finished in {duration:.2f}s, Peak Memory: {peak_memory / 1024 / 1024:.2f} MB")

    return {
        "size": size,
        "profiler": profiler,
        "mode": mode,
        "duration_sec": duration,
        "peak_memory_mb": peak_memory / 1024 / 1024,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=str, help="Comma separated list of sizes to run")
    args = parser.parse_args()

    if args.sizes:
        sizes_to_run = [int(s) for s in args.sizes.split(",")]
    else:
        sizes_to_run = SIZES

    results = []
    base_output_dir = "/tmp/ibis-profiling/benchmarks"
    os.makedirs(base_output_dir, exist_ok=True)

    # Load existing results if any to avoid re-running everything if interrupted
    results_path = os.path.join(base_output_dir, "results.json")
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []

    for size in sizes_to_run:
        data_path = f"/tmp/ibis-profiling/bench_data_{size}.parquet"

        # Generate data if not exists
        if not os.path.exists(data_path):
            print(f"Generating data for {size:,} rows...")
            # For 20M, we need to make sure we don't OOM during generation too
            os.system(f"python3 scripts/generate_bench_data.py --rows {size} --output {data_path}")

        if not os.path.exists(data_path):
            print(f"Failed to generate {data_path}")
            continue

        size_dir = os.path.join(base_output_dir, str(size))
        os.makedirs(size_dir, exist_ok=True)

        # Determine modes based on size
        modes = ["minimal", "full"] if size < 500_000 else ["minimal"]

        for profiler in PROFILERS:
            for mode in modes:
                # SKIP ydata for large sets to avoid OOM
                if profiler == "ydata" and size >= 5_000_000:
                    print(f"Skipping ydata for {size:,} rows (likely to OOM)")
                    continue

                # Check if already run
                if any(
                    r["size"] == size and r["profiler"] == profiler and r["mode"] == mode
                    for r in results
                ):
                    print(f"Skipping {profiler} ({mode}) for {size:,} rows (already in results)")
                    continue

                res = run_benchmark(size, profiler, mode, data_path, size_dir)
                results.append(res)

                # Save intermediate results
                with open(results_path, "w") as f:
                    json.dump(results, f, indent=2)

        # DELETE data_path after all profilers for this size are done
        if os.path.exists(data_path):
            print(f"Deleting {data_path} to save disk space...")
            os.remove(data_path)

    print("\n--- Final Results ---")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
