import ibis
from ibis_profiling import ProfileReport
import os


def generate_fresh():
    data_path = "/tmp/ibis-profiling/sample_data.parquet"
    output_dir = "/tmp/ibis-profiling/sample_reports"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    print(f"Reading data from {data_path}...")
    t = ibis.read_parquet(data_path)

    print("Generating Full Report (Default Theme)...")
    report = ProfileReport(t, title="Ibis Profiling: Full Features Demo")
    report.to_file(os.path.join(output_dir, "full_report.html"))

    print("Generating YData Theme Report...")
    report.to_file(os.path.join(output_dir, "ydata_theme.html"), theme="ydata-like")

    print(f"Fresh reports generated in '{output_dir}'.")


if __name__ == "__main__":
    generate_fresh()
