import os
import json
import subprocess
import sys

TAGS = ["v0.1.6", "dev"]
DATA_PATH = "/tmp/ibis-profiling/backtest_100cols.parquet"
RESULTS_PATH = "/tmp/ibis-profiling/backtest_100cols_v016_vs_dev.json"


def run_single_benchmark_code(mode):
    return f"""
import tracemalloc
import time
import ibis
import gc
import json
import os
import sys

# Ensure we can import the local src
sys.path.insert(0, os.getcwd() + '/src')
from ibis_profiling import ProfileReport

con = ibis.duckdb.connect()
table = con.read_parquet("{DATA_PATH}")

gc.collect()
tracemalloc.start()
start_time = time.perf_counter()

try:
    report = ProfileReport(table, minimal=({mode == "minimal"}))
    _ = report.to_json() # Trigger computation
    duration = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
finally:
    tracemalloc.stop()
    con.disconnect()

print(json.dumps({{"duration": duration, "peak_memory": peak_memory}}))
"""


def main():
    if not os.path.exists(DATA_PATH):
        print(f"Data not found at {DATA_PATH}. Please generate it first.")
        sys.exit(1)

    original_branch = (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    )
    all_results = {}

    try:
        for tag in TAGS:
            print(f"\n===== Testing {tag} =====")
            if tag != "dev":
                # For released tags, we must checkout and sync
                print(f"  Stashing and checking out {tag}...")
                subprocess.run(["git", "stash"], capture_output=True)
                subprocess.run(["git", "checkout", tag], check=True, capture_output=True)
                subprocess.run(
                    ["./run.sh", "uv", "sync", "--all-groups"], check=True, capture_output=True
                )
            else:
                # For dev, we use the current worktree
                print("  (Using current worktree)")

            all_results[tag] = {}
            for mode in ["minimal", "full"]:
                print(f"  Running {mode} mode...")
                cmd = ["./run.sh", "uv", "run", "python", "-c", run_single_benchmark_code(mode)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    output = result.stdout.strip().split("\n")
                    # Try to find the JSON line
                    data = None
                    for line in reversed(output):
                        try:
                            data = json.loads(line)
                            break
                        except Exception:
                            continue
                    if data:
                        all_results[tag][mode] = data
                        print(
                            f"    Done: {data['duration']:.2f}s, {data['peak_memory'] / 1024 / 1024:.2f}MB"
                        )
                    else:
                        print(f"    Failed to parse JSON output: {result.stdout}")
                else:
                    print(f"    Failed: {result.stderr}")

            if tag != "dev":
                # Cleanup tag checkout
                print(f"  Returning to {original_branch} and popping stash...")
                subprocess.run(["git", "checkout", original_branch], capture_output=True)
                subprocess.run(["git", "stash", "pop"], capture_output=True)
                subprocess.run(["./run.sh", "uv", "sync", "--all-groups"], capture_output=True)

    finally:
        # Final safety check to ensure we are back on original branch
        subprocess.run(["git", "checkout", original_branch], capture_output=True)

    print("\n--- Comparison Results (100 Columns) ---")
    v016 = all_results.get("v0.1.6", {})
    dev = all_results.get("dev", {})

    for mode in ["minimal", "full"]:
        m016 = v016.get(mode, {})
        mdev = dev.get(mode, {})
        if m016 and mdev:
            d_diff = ((mdev["duration"] - m016["duration"]) / m016["duration"]) * 100
            mem_diff = ((mdev["peak_memory"] - m016["peak_memory"]) / m016["peak_memory"]) * 100
            print(f"{mode.upper()} Mode:")
            print(
                f"  Duration: {m016['duration']:.2f}s -> {mdev['duration']:.2f}s ({d_diff:+.1f}%)"
            )
            print(
                f"  Memory:   {m016['peak_memory'] / 1024 / 1024:.1f}MB -> {mdev['peak_memory'] / 1024 / 1024:.1f}MB ({mem_diff:+.1f}%)"
            )

    with open(RESULTS_PATH, "w") as f:
        json.dump(all_results, f, indent=2)


if __name__ == "__main__":
    main()
