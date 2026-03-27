import ibis
import pandas as pd
from ibis_profiling import ProfileReport
import base64


def test_offline_rendering_assets():
    # Create a small report
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    table = ibis.memtable(df)
    report = ProfileReport(table)

    # 1. Test offline=True (default)
    html_offline = report.to_html(offline=True)

    # Verify no CDN links
    assert "https://unpkg.com/react" not in html_offline
    assert "https://cdn.tailwindcss.com" not in html_offline

    # Verify CSP
    assert "Content-Security-Policy" in html_offline
    assert "connect-src 'none'" in html_offline

    # Verify local content is present (check for some unique strings in the libraries)
    # React production usually has "React" global
    assert "window.react=window.React" in html_offline.replace(" ", "")

    # 2. Test offline=False
    html_online = report.to_html(offline=False)

    # Verify CDN links ARE present
    assert "https://unpkg.com/react" in html_online
    assert "https://cdn.tailwindcss.com" in html_online

    # Verify SRI hashes
    assert 'integrity="sha384-' in html_online

    # Verify CSP for online mode
    assert "connect-src *" in html_online


def test_to_file_offline_parameter(tmp_path):
    df = pd.DataFrame({"a": [1, 2, 3]})
    table = ibis.memtable(df)
    report = ProfileReport(table)

    output_file = tmp_path / "report.html"
    report.to_file(str(output_file), offline=True)

    with open(output_file, "r") as f:
        content = f.read()

    assert "https://unpkg.com/react" not in content


def test_json_sanitization_xss():
    # Test that </script> tags in data are escaped
    payload = "</script><script>alert('xss')</script>"
    df = pd.DataFrame({"a": [payload]})
    table = ibis.memtable(df)
    report = ProfileReport(table)

    html = report.to_html()

    # The data is base64 encoded in {{REPORT_DATA}}
    # Extract the base64 string
    import re

    match = re.search(r'const ENCODED_REPORT_DATA = "([^"]+)";', html)
    assert match, "Could not find ENCODED_REPORT_DATA in HTML"

    encoded_data = match.group(1)
    decoded_json = base64.b64decode(encoded_data).decode("utf-8")

    # It should be escaped as <\/script> inside the JSON
    assert "</script>" not in decoded_json
    assert "<\\/script>" in decoded_json
