import os
import ibis
from ibis_profiling import ProfileReport


def test_ydata_theme_interactions(tmp_path):
    # Create a small table with numeric columns
    data = {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [5.0, 4.0, 3.0, 2.0, 1.0],
    }
    table = ibis.memtable(data)

    # Run profile with minimal=False
    report = ProfileReport(table, minimal=False, title="Interactions Test")

    output = tmp_path / "report.html"
    report.to_file(str(output), theme="ydata-like")

    assert os.path.exists(output)
    content = output.read_text()

    # Helper to extract and decode Base64 data from HTML
    import base64
    import json
    import re

    def get_decoded_report(html):
        match = re.search(r'const ENCODED_REPORT_DATA = "(.*?)";', html)
        if not match:
            return None
        return json.loads(base64.b64decode(match.group(1)).decode("utf-8"))

    report_data = get_decoded_report(content)
    assert report_data is not None

    # Check for Interactions section in the HTML (static text should still be there)
    assert "Interactions" in content

    # Check that interactions data is embedded in the JSON payload
    assert "interactions" in report_data
    assert "x" in report_data["interactions"]
    assert "y" in report_data["interactions"]["x"]
    assert report_data["interactions"]["x"]["y"][0] == {"x": 1.0, "y": 5.0}


def test_ydata_theme_no_interactions_when_minimal(tmp_path):
    # Create a small table with numeric columns
    data = {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [5.0, 4.0, 3.0, 2.0, 1.0],
    }
    table = ibis.memtable(data)

    # Run profile with minimal=True
    report = ProfileReport(table, minimal=True, title="No Interactions Test")

    output = tmp_path / "report.html"
    report.to_file(str(output), theme="ydata-like")

    assert os.path.exists(output)
    content = output.read_text()

    # Helper to extract and decode Base64 data from HTML
    import base64
    import json
    import re

    def get_decoded_report(html):
        match = re.search(r'const ENCODED_REPORT_DATA = "(.*?)";', html)
        if not match:
            return None
        return json.loads(base64.b64decode(match.group(1)).decode("utf-8"))

    report_data = get_decoded_report(content)
    assert report_data is not None

    # Check that Interactions section is NOT in navItems/interactions (in the embedded JSON it should be empty)
    assert report_data["interactions"] == {}
