import ibis
import polars as pl
from ibis_profiling import ProfileReport
import os


def generate_samples():
    output_dir = "/tmp/ibis-profiling/sample_reports"
    os.makedirs(output_dir, exist_ok=True)

    print("Generating large test dataset (1M rows)...")
    df = pl.DataFrame(
        {
            "id": range(1000000),
            "user__id__metric": [i % 100 for i in range(1000000)],
            "value": [float(i) * 1.5 for i in range(1000000)],
            "category": ["A" if i % 2 == 0 else "B" for i in range(1000000)],
            "is_active": [i % 3 == 0 for i in range(1000000)],
            "complex_col": [[1, 2] if i % 2 == 0 else [3, 4] for i in range(1000000)],
        }
    )

    t = ibis.memtable(df)

    print("Generating Default HTML Report (with duplicates)...")
    report = ProfileReport(
        t, title="Sample Report (Duplicates Enabled)", minimal=False, compute_duplicates=True
    )
    report.to_file(os.path.join(output_dir, "default_with_duplicates.html"))

    print("Generating Minimal HTML Report (without duplicates)...")
    report_min = ProfileReport(
        t, title="Sample Report (No Duplicates)", minimal=True, compute_duplicates=False
    )
    report_min.to_file(os.path.join(output_dir, "minimal_no_duplicates.html"))

    print("Generating YData Theme Report...")
    report_ydata = ProfileReport(
        t, title="Sample Report (YData Theme)", minimal=False, compute_duplicates=True
    )
    report_ydata.to_file(os.path.join(output_dir, "ydata_theme.html"), theme="ydata-like")

    print(f"Sample reports generated in '{output_dir}' directory.")


if __name__ == "__main__":
    generate_samples()
