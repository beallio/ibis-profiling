import ibis
import json
import os
import time
from ibis_profiling import profile


def main():
    data_path = os.getenv("LOAN_DATA_1M_PATH", "/tmp/ibis-profiling/loan_data_1M.parquet")
    output_dir = os.getenv("IBIS_PROFILING_TMP", "/tmp/ibis-profiling")

    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Please run sample creation first.")
        return

    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    start = time.time()
    report = profile(table)
    duration = time.time() - start

    print(f"Ibis 1M Profile completed in {duration:.4f} seconds.")

    result = {"duration": duration, "report": report.to_dict()}

    out_path = os.path.join(output_dir, "ibis_1M_full.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Ibis stats saved to {out_path}")


if __name__ == "__main__":
    main()
