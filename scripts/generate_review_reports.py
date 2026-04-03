import ibis
import polars as pl
from ibis_profiling import ProfileReport
import os


def main():
    # Create a varied dataset to showcase empty string detection
    df = pl.DataFrame(
        {
            "mostly_empty": ["", "", "val1", "", None, "", "val2", "", "", ""],  # 70% empty
            "all_empty": ["", "", "", "", "", "", "", "", "", ""],  # 100% empty
            "mixed_strings": [
                "apple",
                "",
                "banana",
                "cherry",
                None,
                "date",
                "",
                "elderberry",
                "fig",
                "grape",
            ],  # 20% empty
            "numeric_col": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "const_empty": ["", "", "", "", "", "", "", "", "", ""],
        }
    )

    table = ibis.memtable(df)
    report = ProfileReport(table, title="Empty String Review Report")

    # Save both versions
    os.makedirs("/tmp/ibis-profiling/review", exist_ok=True)

    default_path = "/tmp/ibis-profiling/review/empty_review_default.html"
    ydata_path = "/tmp/ibis-profiling/review/empty_review_ydata.html"

    print(f"Generating default report: {default_path}")
    report.to_file(default_path, theme="default")

    print(f"Generating ydata-like report: {ydata_path}")
    report.to_file(ydata_path, theme="ydata-like")

    print("\nGeneration complete.")


if __name__ == "__main__":
    main()
