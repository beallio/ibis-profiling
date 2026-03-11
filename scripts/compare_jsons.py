import sys
from unittest.mock import MagicMock

sys.modules["pkg_resources"] = MagicMock()

import ibis  # noqa: E402
import os  # noqa: E402
from ydata_profiling import ProfileReport as YDataProfile  # noqa: E402
from generate_test_data import generate_fast_loan_data  # noqa: E402


def main():
    n_rows = 10000
    print(f"Generating {n_rows} rows for comparison...")
    df_polars = generate_fast_loan_data(n_rows)
    df_pandas = df_polars.to_pandas()

    # 1. Run Ibis Profiling
    print("Running Ibis Profiling (Full)...")
    table = ibis.memtable(df_polars)
    # Ensure we use the profile function which handles the 2-pass logic
    from ibis_profiling import profile

    ibis_report = profile(table)
    ibis_json_path = "/tmp/ibis-profiling/ibis_comparison.json"
    ibis_report.to_file(ibis_json_path)

    # 2. Run YData Profiling
    print("Running YData Profiling (Full)...")
    ydata_report = YDataProfile(
        df_pandas, explorative=True, interactions=None
    )  # interactions=None means all
    ydata_json_path = "/tmp/ibis-profiling/ydata_comparison.json"
    ydata_report.to_file(ydata_json_path)
    print("\nReports saved to:")
    print(f"Ibis:  {ibis_json_path}")
    print(f"YData: {ydata_json_path}")


if __name__ == "__main__":
    import sys

    sys.path.append(os.path.join(os.getcwd(), "scripts"))
    main()
