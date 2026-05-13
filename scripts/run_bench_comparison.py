import subprocess
import time
import os
import json
import psutil
import argparse
from typing import Dict, Any


def get_peak_memory(pid: int) -> float:
    try:
        proc = psutil.Process(pid)
        # Include children memory
        mem = proc.memory_info().rss
        for child in proc.children(recursive=True):
            try:
                mem += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return mem / (1024 * 1024)  # MB
    except Exception:
        return 0.0


def run_script(script_content: str, label: str) -> Dict[str, Any]:
    script_path = f"/tmp/ibis-profiling/bench_tmp_{label}.py"
    with open(script_path, "w") as f:
        f.write(script_content)

    start_time = time.time()
    cmd = ["./run.sh", "python", script_path]

    proc = subprocess.Popen(cmd)
    peak_mem = 0.0
    while proc.poll() is None:
        peak_mem = max(peak_mem, get_peak_memory(proc.pid))
        time.sleep(0.1)

    duration = time.time() - start_time
    # os.remove(script_path)
    return {"duration": duration, "peak_memory": peak_mem}


def run_ibis(data_path: str, output_path: str) -> Dict[str, Any]:
    print(f"Running Ibis profiling on {data_path}...")
    script = f"""
import ibis
from ibis_profiling import profile
import json
import os

con = ibis.duckdb.connect()
table = con.read_parquet('{data_path}')
report = profile(table)
with open('{output_path}', 'w') as f:
    json.dump(report.to_dict(), f)
"""
    return run_script(script, "ibis")


def run_ydata(data_path: str, output_path: str) -> Dict[str, Any]:
    print(f"Running ydata-profiling on {data_path}...")
    script = f"""
import pandas as pd
from ydata_profiling import ProfileReport
import json
import numpy as np

df = pd.read_parquet('{data_path}')
profile = ProfileReport(df, minimal=True)
stats = profile.get_description()

def clean(obj):
    if isinstance(obj, dict):
        return {{str(k): clean(v) for k, v in obj.items()}}
    if isinstance(obj, (list, tuple)):
        return [clean(x) for x in obj]
    if hasattr(obj, 'item') and not hasattr(obj, 'shape'):
        return obj.item()
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    return str(obj)

out = {{'table': clean(stats.table), 'variables': clean(stats.variables)}}
with open('{output_path}', 'w') as f:
    json.dump(out, f)
"""
    return run_script(script, "ydata")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=str, required=True)
    args = parser.parse_args()

    # Try to format as int if it looks like one, otherwise use as string
    try:
        display_size = f"{int(args.size):,}"
    except ValueError:
        display_size = args.size

    base_dir = f"/tmp/ibis-profiling/benchmarks/{args.size}"
    os.makedirs(base_dir, exist_ok=True)
    data_path = os.path.join(base_dir, "data.parquet")
    ibis_out = os.path.join(base_dir, "ibis_stats.json")
    ydata_out = os.path.join(base_dir, "ydata_stats.json")
    results_out = os.path.join(base_dir, "results.json")

    ibis_res = run_ibis(data_path, ibis_out)
    ydata_res = run_ydata(data_path, ydata_out)

    results = {"size": args.size, "ibis": ibis_res, "ydata": ydata_res}

    with open(results_out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults for {display_size} rows:")
    print(f"Ibis:  {ibis_res['duration']:.2f}s, {ibis_res['peak_memory']:.2f} MB")
    print(f"ydata: {ydata_res['duration']:.2f}s, {ydata_res['peak_memory']:.2f} MB")


if __name__ == "__main__":
    main()
