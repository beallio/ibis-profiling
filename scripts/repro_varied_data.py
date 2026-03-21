import ibis
import pandas as pd
from ibis_profiling import profile
import os


def generate_varied_data():
    """Generates a dataset with edge cases and potentially problematic values."""
    data = {
        # XSS Payloads
        "xss_col": [
            "</script><script>alert('xss')</script>",
            "normal value",
            "<div>test</div>",
            "another one",
        ],
        # All Nulls (Tests MissingEngine and Correlations)
        "all_nulls": [None, None, None, None],
        # Singletons (Tests n_unique robustness)
        "singletons": ["unique1", "unique2", "duplicate", "duplicate"],
        # Numeric with extreme values and NaN (Tests histograms and metrics)
        "numeric_edge": [1.0, 2.0, float("nan"), 4.0],
        # Large decimals or potential overflow candidates
        "large_ints": [2**63 - 1, 0, -(2**63) + 1, 100],
        # Normal columns for baseline
        "normal_num": [10, 20, 30, 40],
        "normal_cat": ["A", "B", "C", "D"],
    }
    # Multiply to get enough rows for histograms (min 20-30 rows usually helps)
    for k in data:
        data[k] = data[k] * 10

    return ibis.memtable(pd.DataFrame(data))


def main():
    output_dir = "/tmp/ibis-profiling/repro_reports"
    os.makedirs(output_dir, exist_ok=True)

    print("Generating varied dataset...")
    table = generate_varied_data()

    # 1. Full Profile (Minimal=False)
    print("Generating FULL profile...")
    full_report = profile(table, minimal=False, title="Varied Data - Full Report")
    full_report.to_file(os.path.join(output_dir, "varied_full.html"))
    full_report.to_file(os.path.join(output_dir, "varied_full.json"))

    # 2. Minimal Profile (Minimal=True)
    print("Generating MINIMAL profile...")
    min_report = profile(table, minimal=True, title="Varied Data - Minimal Report")
    min_report.to_file(os.path.join(output_dir, "varied_minimal.html"))
    min_report.to_file(os.path.join(output_dir, "varied_minimal.json"))

    # 3. Empty Table Case (Tests Finding 5)
    print("Generating EMPTY table profile...")
    empty_df = pd.DataFrame(columns=["a", "b"])
    empty_table = ibis.memtable(empty_df)
    empty_report = profile(empty_table, title="Empty Table Report")
    empty_report.to_file(os.path.join(output_dir, "empty_table.html"))
    empty_report.to_file(os.path.join(output_dir, "empty_table.json"))

    print(f"\nReports generated in: {output_dir}")

    # Quick verification of XSS escaping in one of the HTML files
    with open(os.path.join(output_dir, "varied_full.html"), "r") as f:
        html = f.read()
        if "</script><script>" in html:
            print("❌ XSS VULNERABILITY DETECTED IN OUTPUT!")
        elif "\\u003c/script\\u003e\\u003cscript\\u003e" in html:
            print("✅ XSS Protection Verified: HTML contains escaped sequences.")
        else:
            print("⚠️ Could not find XSS payload in HTML (check script logic).")


if __name__ == "__main__":
    main()
