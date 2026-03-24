import os
import ibis
import pytest
import json
import base64
import re
from ibis_profiling import ProfileReport


def test_large_report_decoding(tmp_path):
    # Generate a large dataset to force a big JSON payload
    # 100 columns with many unique strings
    num_cols = 50
    num_rows = 1000
    data = {}
    for i in range(num_cols):
        # Long strings to bloat the JSON
        data[f"col_{i}"] = [f"Value_{i}_{j}_" + "x" * 100 for j in range(num_rows)]

    table = ibis.memtable(data)

    # Generate report
    report = ProfileReport(table, title="Large Report Test")
    output_file = tmp_path / "large_report.html"
    report.to_file(str(output_file))

    assert os.path.exists(output_file)
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Generated report size: {size_mb:.2f} MB")

    # We want at least 5MB of encoded data to test robustness
    # The HTML will be larger than the raw JSON

    html_content = output_file.read_text(encoding="utf-8")
    match = re.search(r'const ENCODED_REPORT_DATA = "(.*?)";', html_content)
    assert match is not None

    encoded_data = match.group(1)
    encoded_size_mb = len(encoded_data) / (1024 * 1024)
    print(f"Encoded JSON size: {encoded_size_mb:.2f} MB")

    # Verify Python can still decode it (baseline)
    decoded_json = base64.b64decode(encoded_data).decode("utf-8")
    report_data = json.loads(decoded_json)
    assert len(report_data["variables"]) == num_cols


if __name__ == "__main__":
    pytest.main([__file__])
