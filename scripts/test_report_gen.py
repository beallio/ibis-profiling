import ibis
from ibis_profiling import profile
import os
import sys


import argparse


def main():
    parser = argparse.ArgumentParser(description="Generate a test report from a parquet file.")
    parser.add_argument(
        "input",
        nargs="?",
        default="/tmp/ibis-profiling/min_test.parquet",
        help="Path to input parquet file",
    )
    parser.add_argument("--no-minify", action="store_true", help="Disable HTML minification")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Input file {input_path} not found.")
        sys.exit(1)

    print(f"Loading {input_path}...")
    table = ibis.read_parquet(input_path)

    print("Profiling dataset...")
    report = profile(table)

    html_out = "/tmp/ibis-profiling/test_report.html"
    json_out = "/tmp/ibis-profiling/test_report.json"

    minify = not args.no_minify
    print(f"Saving HTML to {html_out} (minify={minify})...")
    report.to_file(html_out, minify=minify)

    print(f"Saving JSON to {json_out}...")
    report.to_file(json_out)

    if os.path.exists(html_out) and os.path.getsize(html_out) > 0:
        print(f"SUCCESS: HTML report generated ({os.path.getsize(html_out)} bytes)")
    else:
        print("FAILURE: HTML report not generated.")
        sys.exit(1)

    if os.path.exists(json_out) and os.path.getsize(json_out) > 0:
        print(f"SUCCESS: JSON report generated ({os.path.getsize(json_out)} bytes)")
    else:
        print("FAILURE: JSON report not generated.")
        sys.exit(1)


if __name__ == "__main__":
    main()
