import ibis
import time
import os
from ibis_profiling import ProfileReport


def main():
    # Use environment variable or default
    data_path = os.getenv("LOAN_DATA_PATH", "/home/beallio/Downloads/loan_data_20M.parquet")
    output_dir = os.getenv("IBIS_PROFILING_TMP", "/tmp/ibis-profiling")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    print(f"Loading {data_path}...")
    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    print("Starting Ibis profile (with histograms)...")
    start_time = time.time()
    report = ProfileReport(table)
    duration = time.time() - start_time
    print(f"Profile completed in {duration:.2f} seconds.")

    # Generate all 5 templates
    templates = ["ydata", "modern", "executive", "dense", "minimal"]
    for temp in templates:
        path = os.path.join(output_dir, f"profile_{temp}.html")
        print(f"Generating {temp} report...")
        with open(path, "w") as f:
            f.write(report.to_html(template=temp))
        print(f"Saved to {path}")


if __name__ == "__main__":
    main()
