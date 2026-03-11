# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "polars",
#   "pyarrow",
#   "numpy",
# ]
# ///
import ibis
import os
import time
from ibis_profiling import profile


def main():
    data_path = "/tmp/ibis-profiling/alert_test_data.parquet"
    if not os.path.exists(data_path):
        print("Data not found. Run generate_alert_data.py first.")
        return

    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    print("Profiling alert test data...")
    start = time.time()
    report = profile(table)
    end = time.time()

    print(f"Profile completed in {end - start:.2f} seconds.")

    out_html = "/tmp/ibis-profiling/profile_alerts.html"
    report.to_file(out_html)
    print(f"Report saved to {out_html}")

    # Quick check of alerts in JSON
    alerts = report.to_dict()["alerts"]
    print(f"Alerts found: {len(alerts)}")
    for a in alerts:
        print(f" - {a['type']} on {a['fields']}")


if __name__ == "__main__":
    main()
