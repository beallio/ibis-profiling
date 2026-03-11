# /// script
# dependencies = [
#   "ydata-profiling",
#   "pandas<3.0",
#   "pyarrow",
# ]
# ///
import json
import pandas as pd
import os
import time
from ydata_profiling import ProfileReport


def main():
    data_path = os.getenv("LOAN_DATA_1M_PATH", "/tmp/ibis-profiling/loan_data_1M.parquet")
    output_dir = os.getenv("IBIS_PROFILING_TMP", "/tmp/ibis-profiling")

    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    df = pd.read_parquet(data_path)

    start = time.time()
    profile = ProfileReport(df, minimal=True)
    stats = profile.get_description()
    duration = time.time() - start

    print(f"ydata 1M Profile completed in {duration:.4f} seconds.")

    # Extract serializable part
    out = {"duration": duration, "table": stats.table, "variables": stats.variables}

    def clean_dict(d):
        if isinstance(d, dict):
            return {str(k): clean_dict(v) for k, v in d.items()}
        elif isinstance(d, (list, tuple)):
            return [clean_dict(x) for x in d]
        elif hasattr(d, "item") and not hasattr(d, "shape"):
            try:
                return d.item()
            except Exception:
                return str(d)
        elif hasattr(d, "isoformat"):
            return d.isoformat()
        elif isinstance(d, (int, float, str, bool, type(None))):
            return d
        else:
            return str(d)

    out_path = os.path.join(output_dir, "ydata_1M_full.json")
    with open(out_path, "w") as f:
        json.dump(clean_dict(out), f, indent=2)
    print(f"ydata stats saved to {out_path}")


if __name__ == "__main__":
    main()
