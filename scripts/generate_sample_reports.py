import ibis
import polars as pl
import os
from ibis_profiling import ProfileReport


def generate_sample_data(output_path):
    # Use Polars for memory-efficient data generation
    df = pl.DataFrame(
        {
            "email_col": (
                ["user@example.com", "support@domain.org", "test.name@company.co.uk"] * 10
            )[:30],
            "url_col": (
                ["https://google.com", "http://localhost:8080/api", "ftp://files.server.net/path"]
                * 10
            )[:30],
            "ip_col": (["192.168.1.1", "8.8.8.8", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"] * 10)[
                :30
            ],
            "phone_col": (["+1-541-754-3010", "(541) 754-3010", "5417543010"] * 10)[:30],
            "uuid_col": (["550e8400-e29b-41d4-a716-446655440000"] * 30),
            "bool_col": (["yes", "no", "y", "n", "true", "false"] * 5),
            "count_col": ([0, 1, 5, 10, 100, 500] * 5),
            "decimal_col": (["1.1", "2.5", "1e-3", "-3.14"] * 8)[:30],
            "ordinal_col": (["low", "medium", "high", "medium", "low"] * 6),
            "string_col": (["just a normal string"] * 30),
        }
    )
    df.write_parquet(output_path)
    return ibis.read_parquet(output_path)


def generate_reports():
    data_path = "/tmp/ibis-profiling/sample_data.parquet"
    output_dir = "/tmp/ibis-profiling/sample_reports"
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    table = generate_sample_data(data_path)

    # 1. Default Theme
    print("Generating Default theme report...")
    report_default = ProfileReport(table, title="Logical Type Demo (Default)")
    report_default.to_file(os.path.join(output_dir, "report_default.html"), theme="default")

    # 2. YData-Like Theme
    print("Generating YData-Like theme report...")
    report_ydata = ProfileReport(table, title="Logical Type Demo (YData-Like)")
    report_ydata.to_file(os.path.join(output_dir, "report_ydata.html"), theme="ydata-like")

    print(f"\nReports generated successfully in: {output_dir}")
    print(f"- Default: {os.path.join(output_dir, 'report_default.html')}")
    print(f"- YData-Like: {os.path.join(output_dir, 'report_ydata.html')}")


if __name__ == "__main__":
    generate_reports()
