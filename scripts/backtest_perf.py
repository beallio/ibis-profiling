import os
import json
import subprocess
import sys

# Tags to test (v0.1.2 is listed twice as it was tagged with and without 'v', let's just use v*)
TAGS = ["v0.1.0", "v0.1.1", "v0.1.2", "v0.1.3", "v0.1.4", "v0.1.5", "v0.1.6"]
DATA_PATH = "/tmp/ibis-profiling/backtest_data.parquet"
RESULTS_PATH = "/tmp/ibis-profiling/backtest_results.json"


def run_single_benchmark(mode):
    # This function is designed to be called by uv run python -c "..."
    # so that it runs in the context of the CURRENT checkout.
    import tracemalloc
    import time
    import ibis
    import gc
    from ibis_profiling import ProfileReport

    con = ibis.duckdb.connect()
    table = con.read_parquet("/tmp/ibis-profiling/backtest_data.parquet")

    gc.collect()
    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        # Standard API for all versions
        report = ProfileReport(table, minimal=(mode == "minimal"))
        output = f"/tmp/ibis-profiling/bench_{mode}.html"
        report.to_file(output)

        duration = time.perf_counter() - start_time
        _, peak_memory = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
        con.disconnect()

    print(json.dumps({"duration": duration, "peak_memory": peak_memory}))


def main():
    if not os.path.exists(DATA_PATH):
        print(f"Data not found at {DATA_PATH}")
        sys.exit(1)

    # Save original branch
    original_branch = (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    )

    all_results = {}

    try:
        for tag in TAGS:
            print(f"\n===== Testing {tag} =====")
            try:
                subprocess.run(["git", "checkout", tag], check=True, capture_output=True)
                # Sync environment for this tag
                # Using ./run.sh uv sync --all-groups
                subprocess.run(
                    ["./run.sh", "uv", "sync", "--all-groups"], check=True, capture_output=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Failed to checkout or sync {tag}: {e}")
                continue

            all_results[tag] = {}

            for mode in ["minimal", "full"]:
                print(f"  Running {mode} mode...")
                try:
                    # Run the benchmark in a separate process to ensure a clean slate and correct imports
                    # We pass the benchmark code as a string to avoid file path issues after checkout
                    cmd = [
                        "./run.sh",
                        "uv",
                        "run",
                        "python",
                        "-c",
                        f"import json; import os; import sys; sys.path.append(os.getcwd()+'/src'); {run_single_benchmark_code(mode)}",
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    # The output should be a JSON string from our print(json.dumps(...))
                    output_lines = result.stdout.strip().split("\n")
                    # Last line should be our JSON
                    data = json.loads(output_lines[-1])
                    all_results[tag][mode] = data
                    print(
                        f"    Done: {data['duration']:.2f}s, {data['peak_memory'] / 1024 / 1024:.2f}MB"
                    )
                except Exception as e:
                    print(f"    Failed {mode} for {tag}: {e}")
                    if hasattr(e, "stdout"):
                        print(e.stdout)
                    if hasattr(e, "stderr"):
                        print(e.stderr)

    finally:
        print(f"\nReturning to {original_branch}")
        subprocess.run(["git", "checkout", original_branch], capture_output=True)
        subprocess.run(["./run.sh", "uv", "sync", "--all-groups"], capture_output=True)

    with open(RESULTS_PATH, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nAll results saved to {RESULTS_PATH}")


def run_single_benchmark_code(mode):
    return f"""
import tracemalloc
import time
import ibis
import gc
import json
import os
try:
    from ibis_profiling import ProfileReport
except ImportError:
    # Older versions might have it differently or need src in path
    import sys
    sys.path.append(os.getcwd()+'/src')
    from ibis_profiling import ProfileReport

con = ibis.duckdb.connect()
table = con.read_parquet("{DATA_PATH}")

gc.collect()
tracemalloc.start()
start_time = time.perf_counter()

try:
    report = ProfileReport(table, minimal=({mode == "minimal"}))
    output = f"/tmp/ibis-profiling/bench_{mode}.html"
    report.to_file(output)

    duration = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
finally:
    tracemalloc.stop()
    con.disconnect()

print(json.dumps({{"duration": duration, "peak_memory": peak_memory}}))
"""


if __name__ == "__main__":
    main()
