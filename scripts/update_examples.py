import ibis
from ibis_profiling import ProfileReport
import os


def update_examples():
    data_path = "/tmp/ibis-profiling/sample_data.parquet"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run generate_bench_data.py first.")
        return

    t = ibis.read_parquet(data_path)

    # Output directories
    html_dir = "examples/html"
    json_dir = "examples/json"
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    print("Generating Full Examples (HTML and JSON)...")
    full_report = ProfileReport(t, title="Ibis Profiling: Full Example")
    full_report.to_file(os.path.join(html_dir, "full_report.html"))
    full_report.to_file(os.path.join(json_dir, "full_report.json"))

    print("Generating Minimal Examples (HTML and JSON)...")
    min_report = ProfileReport(t, title="Ibis Profiling: Minimal Example", minimal=True)
    min_report.to_file(os.path.join(html_dir, "minimal_report.html"))
    min_report.to_file(os.path.join(json_dir, "minimal_report.json"))

    print("Examples updated successfully.")


if __name__ == "__main__":
    update_examples()
